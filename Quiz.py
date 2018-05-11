"""This class represents a quiz. It contains all the questions,
the quiz id and length of quiz. A Quiz keeps track of the current
question it is on and any dropped questions.
"""
class Quiz(object):

    def __init__(self, questions, quiz_name, quiz_id):
        self.questions = questions
        self.name = quiz_name
        self.id = quiz_id
        self.quiz_length = len(questions)
        self.index = 0
        self.score = 0
        self.num_dropped = 0


    def display(self):
        """Displays a question to the terminal by writing the question and
        answer choices. May also drop questions that are not long enough
        """
        # questions that are too short are likely not paresed correctly
        if len(self.questions[self.index][1]) > 10:
            print(self.questions[self.index][1])
            print(self.questions[self.index][2])
        else:
            # drop question so it does not affect score
            self.num_dropped += 1
            self.next_question()
            self.display()


    def choice_is_correct(self, choice):
        """Checks if the user input matches the question answer.
        A correct answer increases the score

        Keyword arguments:
            choice -- user's input

        Returns:
            The correct answer if the user selected the wrong choice
        """
        if (choice == self.questions[self.index][0].replace(" ", "").lower()):
            self.score += 1
            return None
        return self.questions[self.index][0]

    def mark_question(self, db):
        """Marks a question so that a user can study it later

        Keyword arguments:
            db -- a DBManager object
        """
        db.mark_question(self.questions[self.index][1], self.id)

    def question_is_marked(self, db):
        """Checks if a question is marked in the database

        Keyword arguments:
            db -- a DBManager object

        Returns:
            True if the question is marked, False if not
        """
        return db.is_marked(self.questions[self.index][1], self.id)

    def next_question(self):
        """Changes index to next question

        Returns:
            -1 if the index is invalid, this signifies that the quiz is over
        """
        self.index += 1
        if self.index >= self.quiz_length:
            return -1
        return 1

    def get_score(self):
        """
        Returns:
            The user's score on the quiz as a percentage with 100% being
            the max score
        """
        return (self.score / (self.quiz_length - self.num_dropped)) * 100
