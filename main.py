from DBManager import *
from PiazzaQuestions import *
from Constants import *
import os, sys

db = DBManager(DB_NAME)
pq = PiazzaQuestions()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def main(args):
    if (db.isFirstTime()):
        result = 0
        print("(WARNING: credentials are stored unencrypted on disk,"
        + "please ensure your piazza password is not used for any other"
        + "of your accounts))")
        while (result == 0):
            print("Please enter your Piazza Credentials")
            user = input("Email:")
            pwd = input("Password:")
            result = -1
            while (result == -1):
                print("Enter course id, found in web browser")
                print("ex) https://piazza.com/class/*jc9ytz0wynr79*")
                print("where the ** portion is the course id")
                course_id = input("course id:")
                result = pq.firstTimeLogin(user, pwd, course_id)
                clear()
                if (result == 0):
                    print("Username or password incorrect!")
                elif (result == -1):
                    print("Failed to find course with given course id")
                else:
                    result = 1
    else:
        print("logging in...")
        if (pq.loginUser() == -1):
            print("login failed")
            sys.exit(1)
        print("login succesful!")

        print("Searching Piazza for new quizzes...")
        pq.findAllQuizQuestions()

    print("MAIN MENU")

if __name__ == '__main__':
    main(sys.argv)
