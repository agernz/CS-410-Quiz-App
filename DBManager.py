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
            err_file.write("Error: {0} > {1} > {2}", date, msg, e)


    def dbInsertProject(self, name='', description='', start_date='', end_date='', link='', email='', sponsor=''):
        try:
            last_id = self.cur.lastrowid
            self.cur.execute('''INSERT INTO app_project(name, description, start_date, end_date, trello_link, email, sponsor)
                    VALUES(?,?,?,?,?,?,?)''', (name, description, start_date, end_date, link, email, sponsor))
            self.db.commit()
        except Exception as e:
            self.log('Failed to insert project {0}'.format(name), e)

    def isFirstTime(self):
        cursor = self.cur.execute("SELECT USER from FIRST_USE")
        return cursor.fetchone() is None

    # def authenticate():
