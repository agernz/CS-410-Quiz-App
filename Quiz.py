class Quiz(object):

    def __init__(self, questions):
        self.questions = questions
        self.index = 0

    def display(self):
        print(self.questions[self.index])

    def choice_is_correct(self, choice):
        if (choice == self.questions[self.index][0].replace(" ", "").lower()):
            return True
        return False

    def mark_question(self, db):
        db.update_question(self.questions[self.index][1])

    def next_question(self):
        self.index += 1
