from DBManager import *
from PiazzaQuestions import *
from Constants import *
from Quiz import *
import os, sys
import metapy

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
        choice.strip()
        choice = choice_is_valid(choice, i + 4)
        if (choice):
            break

    if choice == i + 4:
        return None

    questions = None
    quiz_name = None
    if choice == i + 2:
        questions = db.get_questions("all")
        quiz_name = ALL_NAME
    elif choice == i + 3:
        questions = db.get_questions("m")
        quiz_name = MARKED_NAME
        if len(questions) == 0:
            clear()
            print("No questions have been marked")
            input_wait()
            return None
    else:
        questions = db.get_questions(quizzes[choice - 1][0])
        quiz_name = quizzes[choice - 1][1]

    check_db_return(questions)

    return Quiz(questions, quiz_name)

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
        user_input.strip()
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

""" Creates a directory /search/<quiz name>/ which contains
a dat file and line.toml so that the quiz can be searched using
MeTA

If the quiz name is ALL_NAME or MARKED_NAME, then the directory
is overwritten since the data for these quizzes can change

returns True on success, or False if an error occurs
"""
def create_dataset_if_not_exist(quiz):
    directory = "{0}/{1}".format(SEARCH_DIR, quiz.name.replace(" ", "_"))
    if os.path.isdir(directory) and (quiz.name != ALL_NAME and quiz.name != MARKED_NAME):
        return True

    try:
        if not os.path.isdir(directory):
            os.makedirs(directory)
    except Exception as e:
        print(e)
        return False

    try:
        data_file = open("{0}/{1}.dat".format(directory, quiz.name.replace(" ", "_")), 'w')
        meta_file = open("{0}/{1}.dat".format(directory, "metadata"), 'w')
        for question in quiz.questions:
            # questions that are too short are likely not paresed correctly
            if len(question[1]) > 10:
                data_file.write("{0}\n".format(question[1]))
                meta_file.write("{0}\n".format(question[1]))
        data_file.close()
        meta_file.close()

        line_file = open("/".join((directory, LINE_FILE)), 'w')
        line_file.write("type = 'line-corpus'\nmetadata = [{name = 'content', type = 'string'}]")
        line_file.close()
    except Exception as e:
        print(e)
        return False
    return True

""" Updates the config.toml dataset field with the given
quiz name

returns True on success, false if fials to open file
"""
def setup_config(quiz_name):
    try:
        conf_file = open("config.toml", 'r')
        lines = conf_file.readlines()
        conf_file.close()

        for i in range(len(lines)):
            if lines[i].startswith("index"):
                lines[i] = "index = 'idx-{0}'\n".format(quiz_name.replace(" ", "_"))
            if lines[i].startswith("dataset"):
                lines[i] = "dataset = '{0}'\n".format(quiz_name.replace(" ", "_"))

        conf_file = open("config.toml", 'w')
        with conf_file:
            conf_file.writelines(lines)
    except Exception as e:
        print(e)
        return False
    return True

""" Creates a Quiz object that contains questions from
user's query. Ranking is done using metapy. The questions
found are presented and the user has the option to take the quiz
or not.

Returns Quiz object
"""
def select_questions_from_quiz(query, num_questions):
    idx = metapy.index.make_inverted_index("config.toml")
    ranker = metapy.index.OkapiBM25()
    search = metapy.index.Document()
    search.content(query.strip())

    top_questions = ranker.score(idx, search, num_results=num_questions)
    quiz_questions = []
    for num, (d_id, _) in enumerate(top_questions):
        content = idx.metadata(d_id).get('content')
        question = db.get_questions_from_question(content)
        if question != -1:
            print(content)
            quiz_questions.append(question)

    if len(quiz_questions) == 0:
        print("No questions found relating to query")
        input_wait()
        return None

    if (input("\nTake Quiz? (y/n): ").strip().lower() != 'y'):
        return None

    return Quiz(quiz_questions, None)

""" Perform topic modeling using quiz data from
user selected quiz. Lists all 10 topics generated and
ask user to select a topic

Returns user selected topic
"""
def select_generated_topics():
    output = "out"
    _num_topics = 10
    _k = 3

    fidx = metapy.index.make_forward_index("config.toml")
    dset = metapy.learn.Dataset(fidx)
    lda_inf = metapy.topics.LDAGibbs(dset, num_topics=_num_topics, alpha=1.0, beta=0.01)
    lda_inf.run(num_iters=500)
    lda_inf.save(output)
    model = metapy.topics.TopicModel(output)

    while (1):
        topics = []
        for topic_id in range(_num_topics):
            query = ""
            print(topic_id + 1, ")", end=' ')
            for pr in model.top_k(tid=topic_id, k=_k):
                term = fidx.term_text(pr[0])
                print(term, end=' ')
                query += term + " "
            topics.append(query)
            print()

        choice = input("Select an option (1-{0}): ".format(_num_topics))
        # check validity of input
        choice.strip()
        choice = choice_is_valid(choice, _num_topics)
        if (choice):
            break

    return topics[choice - 1]

""" Performs setup needed after a user selcts a quiz
to either search or perform topic analysis on. Creates
dataset if it does not exist and sets config file to that
dataset

Returns True on success, false if there was an error
"""
def setup_metapy_data(quiz):
    if not (create_dataset_if_not_exist(quiz)):
        print("Failed to create search index")
        input_wait()
        return False
    if not (setup_config(quiz.name)):
        print("Could not open config.toml")
        input_wait()
        return False
    return True


def main_menu():
    choice = 0
    while (choice != 4):
        clear()
        print( "QuizME\n" +
        "------------\n" +
        "1) Select Quiz\n2) Search Questions\n3) Generate Sub-quizzes\n4) Exit")
        choice = input("Select an option (1-4): ")
        # check validity of input
        choice.strip()
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
            quiz = select_quiz()
            if quiz:
                clear()
                if not setup_metapy_data(quiz):
                    continue
                print("Search for specific questions in %s\n" % quiz.name)
                query = input("Enter query: ")
                quiz = select_questions_from_quiz(query, len(quiz.questions))
                if quiz:
                    take_quiz(quiz)
        elif choice == 3:
            clear()
            quiz = select_quiz()
            if quiz:
                clear()
                if not setup_metapy_data(quiz):
                    continue
                query = select_generated_topics()
                quiz = select_questions_from_quiz(query, len(quiz.questions))
                if quiz:
                    take_quiz(quiz)
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
