from DBManager import *
from PiazzaQuestions import *
from Constants import *
from Quiz import *
import os, sys

db = DBManager(DB_NAME)
pq = PiazzaQuestions()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def input_wait():
    input("\nPress enter to continue...")
    clear()

def check_db_return(result):
    if (result == -1):
        print("Database error, check errors.txt for problem.")
        exit(1)

def choice_is_valid(choice, max):
    if (not choice.isdigit()):
        print("Invalid choice selected, please enter a number 1-{0}".format(max))
        input_wait()
        return 0

    choice = int(choice)
    if (choice > max):
        print("Invalid choice selected, please enter a number 1-{0}".format(max))
        input_wait()
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
    quizzes = db.get_quizzes()
    check_db_return(quizzes)

    while (1):
        # list all quiz choices
        i = 0
        for i in range(0, len(quizzes)):
            print("{0}) {1}".format(i + 1, quizzes[i][1]))
        # option for all quizzes
        print("{0}) All".format(i + 2))
        # option for marked questions
        print("{0}) Marked Questions".format(i + 3))
        # exit option
        print("{0}) Back".format(i + 4))

        choice = input("Select an option (1-{0}): ".format(i + 4))
        # check validity of input
        choice.replace(" ", "")
        choice = choice_is_valid(choice, i + 4)
        if (choice):
            break

    if choice == i + 4:
        return None

    questions = None
    if choice == i + 2:
        questions = db.get_questions("all")
    elif choice == i + 3:
        questions = db.get_questions("m")
        if len(questions) == 0:
            clear()
            print("No questions have been marked")
            input_wait()
            return None
    else:
        questions = db.get_questions(quizzes[choice - 1][0])

    check_db_return(questions)

    return Quiz(questions)

def take_quiz(quiz):
    clear()
    quizzing = 1
    while (quizzing != -1):
        if quiz.question_is_marked(db):
            print("*This question has been marked*\n")
        quiz.display()
        print ("\n(Enter '{0}' to exit the quiz, or '{1}' to mark/unmark question)\n".format(
        EXIT_QUIZ, MARK_QUESTION))
        user_input = input("Your Answer: ")
        user_input.replace(" ", "")
        if user_input == EXIT_QUIZ:
            break
        if user_input == MARK_QUESTION:
            quiz.mark_question(db)
            clear()
            continue
        user_input = user_input.lower()
        quiz_answer = quiz.choice_is_correct(user_input)
        if  quiz_answer == None:
            print("You are correct!")
        else:
            print("Incorrect, the correct answer was: ", quiz_answer)

        quizzing = quiz.next_question()
        input_wait()

    clear()
    print("Your score was: {0:.2f}%".format(quiz.get_score()))
    input_wait()

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
    clear()


def main(args):
    # if (db.is_first_time()):
    #     register_user()
    #
    # else:
    #     print("logging in...")
    #     if (pq.login_user() == -1):
    #         print("login failed")
    #         sys.exit(1)
    #     print("login succesful!")
    #
    #     print("Searching Piazza for new quizzes...")
    #     pq.find_all_quiz_questions()
    #
    # input_wait()

    main_menu()

if __name__ == '__main__':
    main(sys.argv)
