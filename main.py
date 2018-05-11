from DBManager import *
from PiazzaQuestions import *
from Constants import *
from Quiz import *
import os, sys
import metapy

db = DBManager(DB_NAME)
pq = PiazzaQuestions()

def clear():
    """Clears the terminal using windows or linux command"""
    os.system('cls' if os.name == 'nt' else 'clear')

def input_wait():
    """Wait for user to press return before proceeding"""
    input("\nPress enter to continue...")
    clear()

def check_db_return(result):
    """Use to close program if the database returns an error

    Keyword arguments:
        result -- return value from DBManager function
    """
    if (result == -1):
        print("Database error, check errors.txt for problem.")
        exit(1)

def choice_is_valid(choice, max):
    """Checks that choice is a valid option by ensuring
    it is a digit and that it lies between 0 and max

    Keyword arguments:
        choice -- user input
        max -- max value choice can be

    Returns:
        returns the choice if it is valid, 0 if choice was invalid
    """
    if (not choice.isdigit()):
        print("Invalid choice selected, please enter a number 1-{0}".format(max))
        input_wait()
        return 0

    choice = int(choice)
    if (choice > max or choice <= 0):
        print("Invalid choice selected, please enter a number 1-{0}".format(max))
        input_wait()
        return 0
    return choice

def register_user():
    """Attmpts to register a user by asking them for their piazza credentials
    and course id. If user credentials or course id do not work, the user
    will be prompted to enter their credentials or course id again.
    After a succesful login, the credentials will be stored in the
    database and quizzes will be pulled from piazza
    """
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
    """Outputs a numbered list of all the quiz options the user can pick
    from including a category for all quizzes, marked questions, and an
    optiont to return to the main main_menu.

    Returns:
        A Quiz object containing all the quiz questions or None
        if the user does not select a quiz or the user selcts
        marked questions and no question have been marked
    """
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
    quiz_id = None
    if choice == i + 2:
        questions = db.get_questions("all")
        quiz_name = ALL_NAME
    elif choice == i + 3:
        questions = db.get_questions("m")
        quiz_name = MARKED_NAME
        quiz_id = MARK_QUESTION
        if len(questions) == 0:
            clear()
            print("No questions have been marked")
            input_wait()
            return None
    else:
        questions = db.get_questions(quizzes[choice - 1][0])
        quiz_name = quizzes[choice - 1][1]
        quiz_id = quizzes[choice - 1][0]

    check_db_return(questions)

    return Quiz(questions, quiz_name, quiz_id)

def take_quiz(quiz):
    """Quizzes user on all questions in quiz. During the quiz, the user can
    mark a question or quit the quiz. When the user enters their answer,
    it will be reported whether their answer was correct or incorrect. If
    incorrect, the correct answer will be displayed. At the end of the quiz,
    the user's score is reported

    Keyword arguments:
        quiz -- a quiz object
    """
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

def create_dataset_if_not_exist(quiz):
    """Creates a directory /search/<quiz name>/ which contains
    a dat file and line.toml so that the quiz can be searched using
    MeTA.
    If the quiz name is ALL_NAME or MARKED_NAME, then the directory
    is overwritten since the data for these quizzes can change

    Keyword arguments:
        quiz -- a Quiz object

    Returns:
        True on success, or False if an error occurs
    """
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

def setup_config(quiz_name):
    """Updates the config.toml index and dataset field with the formatted
    quiz_name. This directs metapy to use the correct files

    Keyword arguments:
        quiz_name -- the name of the quiz

    Returns:
        True on success, false if fials to open file
    """
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

def setup_metapy_data(quiz):
    """Performs setup needed after a user selcts a quiz
    to either search or perform topic analysis on. Creates
    dataset if it does not exist and sets config file to that
    dataset

    Returns:
        True on success, false if there was an error
    """
    if not (create_dataset_if_not_exist(quiz)):
        print("Failed to create search index")
        input_wait()
        return False
    if not (setup_config(quiz.name)):
        print("Could not open config.toml")
        input_wait()
        return False
    return True

def select_questions_from_quiz(query, quiz):
    """Creates a Quiz object that contains questions from
    user's query. Ranking is done using metapy. The questions
    found are presented and the user has the option to take the quiz
    or not.

    Keyword arguments:
        query -- user input, search terms
        quiz -- a Quiz object to query on

    Returns:
        A Quiz object containing the queried questions
    """
    idx = metapy.index.make_inverted_index("config.toml")
    ranker = metapy.index.OkapiBM25()
    search = metapy.index.Document()
    search.content(query.strip())

    top_questions = ranker.score(idx, search, num_results=len(quiz.questions))
    quiz_questions = []
    for num, (d_id, _) in enumerate(top_questions):
        content = idx.metadata(d_id).get('content')
        question = db.get_questions_from_question(content, quiz.id)
        if question != -1:
            print(content)
            quiz_questions.append(question)

    if len(quiz_questions) == 0:
        print("No questions found relating to query")
        input_wait()
        return None

    if (input("\nTake Quiz? (y/n): ").strip().lower() != 'y'):
        return None

    return Quiz(quiz_questions, None, None)

def select_generated_topics():
    """Perform topic modeling using quiz data from
    user selected quiz. Lists 10 generated topics and
    ask user to select a topic. The return value of this function
    should be passed to select_questions_from_quiz to generate quiz questions
    pertaining to the topic

    Returns:
        The user selected topic
    """
    print("Generating Quiz Topics...")

    output = "out"
    _num_topics = 10
    _k = 3

    fidx = metapy.index.make_forward_index("config.toml")
    dset = metapy.learn.Dataset(fidx)
    lda_inf = metapy.topics.LDAGibbs(dset, num_topics=_num_topics, alpha=1.0, beta=0.01)
    lda_inf.run(num_iters=500)
    lda_inf.save(output)
    model = metapy.topics.TopicModel(output)

    clear()

    while (1):
        topics = []
        for topic_id in range(_num_topics):
            query = ""
            print("{0})".format(topic_id + 1), end=' ')
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

def main_menu():
    """Displays a menu for the user to interact with:
    CS 410 Quiz App
    ------------
    1) Select Quiz
    2) Search Questions
    3) Generate Sub-quizzes
    4) Exit
    The user must select 1 of the 4 options, if their input is invalid they
    will be prompted again
    Select Quiz - user picks a quiz to take
    Search Questions - user selects a quiz then enters a query for what
        questions to be quizzed on
    Generate Sub-quizzes - user selects a quiz to generate topics from.
        The top 10 topics are found and the user picks one. The user then given
        questions related to the topic
    """
    choice = 0
    while (choice != 4):
        clear()
        print( "CS 410 Quiz App\n" +
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
                quiz = select_questions_from_quiz(query, quiz)
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
                clear()
                quiz = select_questions_from_quiz(query, quiz)
                if quiz:
                    take_quiz(quiz)
    clear()


def main():
    """If it is the user's first time, the database is set up and the user
    is asked to register. If they have already registered, they will be
    automatically logged in. They then have the option to search piazza for
    new quizzes. The user can still use the program without logging in, but
    they must already be registered. No login means they cannot get new
    quizzes from piazza
    """
    if (db.is_first_time()):
        db.create_tables()
        register_user()

    else:
        print("logging in...")
        if (pq.login_user() != -1):
            print("login succesful!")

            if (input("\nSeach Piazza for new quizzes? (y/n): ").strip().lower() == 'y'):
                clear()
                print("Searching Piazza for new quizzes...")
                pq.find_all_quiz_questions()
                input_wait()
        else:
            if (input("\nlogin failed, continue without logging in? (y/n): ").strip().lower() != 'y'):
                register_user()
                input_wait()
    main_menu()

if __name__ == '__main__':
    main()
