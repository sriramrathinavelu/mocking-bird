from mocktest.models import UserQuestion
from mocktest.models import QuestionBank
from BaseTest import BaseTest


class LinearByTime(BaseTest):

    def __init__(self, *args, **kwds):
        super(LinearByTime, self).__init__(*args, **kwds)

    def __getLastQuestion(self):
        lastQuestion = UserQuestion.objects.\
                        filter(username=self.username,
                               companyid=self.companyId,
                               positionid=self.positionId).limit(1)
        if lastQuestion:
            return lastQuestion.questionid
        return None

    def getQuestions(self, numQ=3):
        # Find the last question asked for that user
        lastQuestion = self.__getLastQuestion()
        questionsList = []
        # Find numQ questions later than the last question
        if lastQuestion:
            questions = QuestionBank.objects.\
                filter(companyid=self.companyId,
                       positionid=self.positionId,
                       questionid__gt=lastQuestion).limit(numQ)
            questionsList = [q for q in questions]
            if len(questions) < numQ:
                # If not go back and add questions at the beginning
                questions = QuestionBank.objects.\
                                         filter(companyid=self.companyId,
                                                positionid=self.positionId).\
                                         limit(numQ-len(questions))
                for q in questions:
                    questionsList.append(q)
        else:
            # Maybe there were no test taken for this
            # company/position by the user
            questions = QuestionBank.objects.\
                                     filter(companyid=self.companyId,
                                            positionid=self.positionId).\
                                     limit(numQ)
            questionsList = [q for q in questions]
        self.numQ = len(questions)
        self.questions = questionsList
