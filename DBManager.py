import sqlite3 as sql
import os, time

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
        err_file = open('errors.txt', 'a')
        with err_file:
            date = "".join(time.strftime('%m/%d/%Y'))
            try:
                err_file.write("Error: {0} > {1} > {2}\n".format(date, msg, e))
            except Exception as e:
                # could print something out here
                pass

    """ Write user credentials to database

    Returns -1 on error
    """
    def store_credentials(self, username, password, course_id):
        try:
            last_id = 0
            self.cur.execute('''INSERT OR REPLACE INTO FIRST_USE(ID, USER, PWD, COURSEID)
                    VALUES(?,?,?,?)''', (last_id, username, password, course_id))
            self.db.commit()
        except Exception as e:
            self.log('Failed to store credentials for {0}'.format(username), e)
            return -1;

    """ Add a new Quiz to database if it does not already exists

    Returns -1 on error, 0 if Quiz already exists
    """
    def store_quiz(self, nr, date, title):
        try:
            cursor = self.cur.execute("SELECT ID FROM QUIZZES")
            for row in cursor:
                if row[0] == nr:
                    return 0
        except Exception as e:
            self.log('Failed to get quiz {0} from database'.format(title), e)
            return -1;

        try:
            self.cur.execute('''INSERT INTO QUIZZES(ID, NAME, CREATED)
                    VALUES(?,?,?)''', (nr, title, date))
            self.db.commit()
        except Exception as e:
            self.log('Failed to insert quiz {0}'.format(title), e)
            return -1;

    """ Adds an array of questions (as tuples) to the database

    Returns -1 on error
    """
    def store_questions(self, questions):
        try:
            self.cur.executemany('''INSERT INTO QUESTIONS(ANSWER, QUESTION, CHOICES, NR, MARKED)
                    VALUES(?,?,?,?,?)''', questions)
            self.db.commit()
        except Exception as e:
            self.log('Failed to insert questions', e)
            return -1;

    """ marks a specific queston by setting column MARKED to 1

    Returns -1 on error
    """
    def mark_question(self, question):
        try:
            self.cur.execute('''UPDATE QUESTIONS SET MARKED=1 WHERE QUESTION=question''')
            self.db.commit()
        except Exception as e:
            self.log('Failed to mark question {0}'.format(question), e)
            return -1;

    """ Gets user credentials from database to login

    Returns -1 on error or a tuple: (username, password, course ID)
    """
    def get_credentials(self):
        try:
            cursor = self.cur.execute("SELECT * FROM FIRST_USE LIMIT 1")
            return cursor.fetchone()
        except Exception as e:
            self.log('Failed to get user credentials', e)
            return -1;

    """ Gets a list of quizzes from database

    Returns -1 on error or a list of quizzes as tuples
    """
    def get_quizzes(self):
        try:
            cursor = self.cur.execute("SELECT * FROM QUIZZES")
            return cursor.fetchall()
        except Exception as e:
            self.log('Failed to get quizzes', e)
            return -1;

    """ Gets a list of questions from the database that
    match a specific quiz. If quiz_id is 'all', then gets all
    quiz questions. If quiz_id is 'm', get marked questions

    Returns -1 on error or a list of questions as tuples
    """
    def get_questions(self, quiz_id):
        try:
            cursor = None
            if (quiz_id == "all"):
                cursor = self.cur.execute("SELECT * FROM QUESTIONS")
            elif (quiz_id == "all"):
                cursor = self.cur.execute("SELECT * FROM QUESTIONS WHERE MARKED=1")
            else:
                cursor = self.cur.execute("SELECT * FROM QUESTIONS WHERE NR={0}".format(quiz_id))
            return cursor.fetchall()
        except Exception as e:
            self.log('Failed to get questions', e)
            return -1;

    def is_first_time(self):
        cursor = self.cur.execute("SELECT USER from FIRST_USE")
        return cursor.fetchone() is None
