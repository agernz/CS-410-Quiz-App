import sqlite3 as sql
import os, time
from Constants import *

"""This class handles all database interactions
Any errors are logged to errors.txt
"""
class DBManager(object):

    def __init__(self, db_name):
        try:
            self.db = sql.connect(db_name);
            self.cur = self.db.cursor()
        except Exception as e:
            self.log('Could not connect to database', e)

    def __del__(self):
        self.db.close();

    def log(self, msg, e):
        """Logs an error to errors.txt with the format:
        Error > date > provided message > python error

        Keyword arguments:
            msg -- a descriptive message for what happned
            e -- the error thrown
        """
        err_file = open('errors.txt', 'a')
        with err_file:
            date = "".join(time.strftime('%m/%d/%Y'))
            try:
                err_file.write("Error: {0} > {1} > {2}\n".format(date, msg, e))
            except Exception as e:
                # could print something out here
                pass

    def store_credentials(self, username, password, course_id):
        """Writes user credentials to database table FIRST_USE

        Keyword arguments:
            username -- user's piazza email
            password -- user's piazza password
            course_id -- piazza course id for class

        Returns:
            -1 on error
        """
        try:
            last_id = 0
            self.cur.execute("""INSERT OR REPLACE INTO FIRST_USE(ID, USER, PWD, COURSEID)
                    VALUES(?,?,?,?)""", (last_id, username, password, course_id))
            self.db.commit()
        except Exception as e:
            self.log('Failed to store credentials for {0}'.format(username), e)
            return -1;

    def store_quiz(self, quiz_id, date, title):
        """Add a new Quiz to database table QUIZZES if it does not already exists

        Keyword arguments:
            quiz_id -- numeric key that identifies piazza post
            date -- date of piazza post
            title -- Title of piazza post

        Returns:
            -1 on error, 0 if Quiz already exists
        """
        try:
            cursor = self.cur.execute("""SELECT ID FROM QUIZZES""")
            for row in cursor:
                if row[0] == quiz_id:
                    return 0
        except Exception as e:
            self.log('Failed to get quiz {0} from database'.format(title), e)
            return -1;

        try:
            self.cur.execute("""INSERT INTO QUIZZES(ID, NAME, CREATED)
                    VALUES(?,?,?)""", (quiz_id, title, date))
            self.db.commit()
        except Exception as e:
            self.log('Failed to insert quiz {0}'.format(title), e)
            return -1;

    def store_questions(self, questions):
        """Writes an array of questions (as tuples) to the database table QUESTIONS

        Returns:
            -1 on error
        """
        try:
            self.cur.executemany("""INSERT INTO QUESTIONS(ANSWER, QUESTION, CHOICES, NR, MARKED)
                    VALUES(?,?,?,?,?)""", questions)
            self.db.commit()
        except Exception as e:
            self.log('Failed to insert questions', e)
            return -1;

    def mark_question(self, question, quiz_id):
        """Marks a specific queston by setting column MARKED to 1 in QUESTIONS
        table. If the question is already marked, than it is unmarked

        Keyword arguments:
            question -- question string
            quiz_id -- numeric key that identifies piazza post

        Returns:
            -1 on error
        """
        try:
            if (quiz_id and quiz_id != MARK_QUESTION):
                if (self.is_marked(question, quiz_id)):
                    self.cur.execute("""UPDATE QUESTIONS SET MARKED=0 WHERE NR={0} AND QUESTION='{1}'""".format(quiz_id, question))
                else:
                    self.cur.execute("""UPDATE QUESTIONS SET MARKED=1 WHERE NR={0} AND QUESTION='{1}'""".format(quiz_id, question))
            else:
                if (self.is_marked(question, quiz_id)):
                    self.cur.execute("""UPDATE QUESTIONS SET MARKED=0 WHERE QUESTION='{0}'""".format(question))
                else:
                    self.cur.execute("""UPDATE QUESTIONS SET MARKED=1 WHERE QUESTION='{0}'""".format(question))
            self.db.commit()
        except Exception as e:
            self.log('Failed to mark question {0}'.format(question), e)
            return -1;

    def is_marked(self, question, quiz_id):
        """Checks if a question has been marked

        Keyword arguments:
            question -- question string
            quiz_id -- numeric key that identifies quiz

        Returns:
            -1 on error, True if marked, false if not
        """
        try:
            marked = None
            if (quiz_id and quiz_id != MARK_QUESTION):
                marked = self.cur.execute("""SELECT MARKED FROM QUESTIONS WHERE NR={0} AND QUESTION='{1}'""".format(quiz_id, question))
            else:
                marked = self.cur.execute("""SELECT MARKED FROM QUESTIONS WHERE QUESTION='{0}'""".format(question))
            return marked.fetchone()[0] == 1
        except Exception as e:
            self.log('Failed to check if a question is marked {0}'.format(question), e)
            return -1;

    def get_credentials(self):
        """Gets user credentials from database to login

        Returns:
            -1 on error or a tuple: (username, password, course ID)
        """
        try:
            cursor = self.cur.execute("""SELECT * FROM FIRST_USE LIMIT 1""")
            return cursor.fetchone()
        except Exception as e:
            self.log('Failed to get user credentials', e)
            return -1;

    def get_quizzes(self):
        """Gets a list of all quizzes from database

        Returns:
            -1 on error or a list of quizzes as tuples, (quiz_id, quiz title, date posted)
        """
        try:
            cursor = self.cur.execute("""SELECT * FROM QUIZZES""")
            return cursor.fetchall()
        except Exception as e:
            self.log('Failed to get quizzes', e)
            return -1;

    def get_questions(self, quiz_id):
        """Gets a list of questions from the database that
        match a specific quiz. If quiz_id is 'all', then gets all
        quiz questions. If quiz_id is 'm', get marked questions. Otherwise
        gets all question from quiz that matches quiz_id

        Keyword arguments:
            quiz_id -- numeric key that identifies quiz

        Returns:
            -1 on error or a list of questions as tuples
            [(answer, question, choices, quiz_id, marked),]
        """
        try:
            cursor = None
            if (quiz_id == "all"):
                cursor = self.cur.execute("""SELECT * FROM QUESTIONS""")
            elif (quiz_id == "m"):
                cursor = self.cur.execute("""SELECT * FROM QUESTIONS WHERE MARKED=1""")
            else:
                cursor = self.cur.execute("""SELECT * FROM QUESTIONS WHERE NR={0}""".format(quiz_id))
            return cursor.fetchall()
        except Exception as e:
            self.log('Failed to get questions', e)
            return -1;

    def get_questions_from_question(self, question, quiz_id):
        """Selects a Question from database that matches the inputted question.
        If the question has an NR, than it will select questions from that specific quiz.
        NR can also be 'M' for marked. If it is none it will search all questions

        Keyword arguments:
            question -- question string
            quiz_id -- numeric key that identifies quiz

        Returns:
            -1 on error, database question as tuple on success
            (answer, question, choices, quiz_id, marked)
        """
        try:
            cursor = None
            if (quiz_id == MARK_QUESTION):
                cursor = self.cur.execute("""SELECT * FROM QUESTIONS WHERE MARKED=1 AND QUESTION='{0}'""".format(question))
            elif (quiz_id):
                cursor = self.cur.execute("""SELECT * FROM QUESTIONS WHERE NR={0} AND QUESTION='{1}'""".format(quiz_id, question))
            else:
                cursor = self.cur.execute("""SELECT * FROM QUESTIONS WHERE QUESTION='{0}'""".format(question))
            return cursor.fetchone()
        except Exception as e:
            self.log('Failed to get questions from question {0}'.format(question), e)
            return -1;

    def is_first_time(self):
        """Checks if a user has logged in before

        Returns:
            True if user's has no stored credentials, False if user has
            logged in before
        """
        cursor = self.cur.execute("""SELECT USER from FIRST_USE""")
        return cursor.fetchone() is None
