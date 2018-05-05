class Quiz(object):

    def __init__(self, questions, quiz_name):
        self.name = quiz_name
        self.questions = questions
        self.quiz_length = len(questions)
        self.index = 0
        self.score = 0


    def display(self):
        print(self.questions[self.index][1])
        print(self.questions[self.index][2])

    def choice_is_correct(self, choice):
        if (choice == self.questions[self.index][0].replace(" ", "").lower()):
            self.score += 1
            return None
        return self.questions[self.index][0]

    def mark_question(self, db):
        db.mark_question(self.questions[self.index][1])

    def question_is_marked(self, db):
        return db.is_marked(self.questions[self.index][1])

    def next_question(self):
        self.index += 1
        if self.index >= self.quiz_length:
            return -1
        return 1

    def get_score(self):
        return (self.score / self.quiz_length) * 100
