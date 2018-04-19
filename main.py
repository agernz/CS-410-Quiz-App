from DBManager import *
from PiazzaQuestions import *
from Constants import *
import os, sys

db = DBManager(DB_NAME)
pq = PiazzaQuestions()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def choice_is_valid(choice, max):
    if (not choice.isdigit()):
        print("Invalid choice selected, please enter a number 1-{0}".format(max))
        input("Press  enter to continue...")
        clear()
        return 0

    choice = int(choice)
    if (choice > max):
        print("Invalid choice selected, please enter a number 1-{0}".format(max))
        input("Press  enter to continue...")
        clear()
        return 0
    return choice

def register_user():
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
            print("Enter course ID, found in web browser")
            print("ex) https://piazza.com/class/*jc9ytz0wynr79*")
            print("where the ** portion is the course ID")
            course_id = input("course id:")
            result = pq.first_time_login(user, pwd, course_id)
            clear()
            if (result == 0):
                print("Username or password incorrect!")
            elif (result == -1):
                print("Failed to find course with given course ID")
            else:
                result = 1

def select_quiz():
    quiz = None
    quizzes = db.get_quizzes()

    while (1):
        # list all quiz choices
        i = 0
        for i in range(0, len(quizzes)):
            print("{0}) {1}".format(i + 1, quizzes[i][1]))
        # option for all quizzes
        print("{0}) All".format(i + 2))
        print("{0}) Back".format(i + 3))

        choice = input("Select an option (1-{0}): ".format(i + 3))
        # check validity of input
        choice.replace(" ", "")
        choice = choice_is_valid(choice, i + 3)
        if (choice):
            break

    return quiz

def take_quiz(quiz):
    print(quiz)


def main_menu():
    choice = 0
    while (choice != 4):
        clear()
        print( "QuizME\n" +
        "------------\n" +
        "1) Select Quiz\n2) Search Questions\n3) Generate Sub-quizzes\n4) Exit")
        choice = input("Select an option (1-4): ")
        # check validity of input
        choice.replace(" ", "")
        choice = choice_is_valid(choice, 4)
        if (not choice):
            continue

        if choice == 1:
            clear()
            quiz = select_quiz()
            if quiz:
                take_quiz(quiz)
        elif choice == 2:
            clear()

        elif choice == 3:
            clear()


def main(args):
    if (db.is_first_time()):
        register_user()

    else:
        print("logging in...")
        if (pq.login_user() == -1):
            print("login failed")
            sys.exit(1)
        print("login succesful!")

        print("Searching Piazza for new quizzes...")
        pq.find_all_quiz_questions()

    input("Press  enter to continue...")

    main_menu()

if __name__ == '__main__':
    main(sys.argv)
