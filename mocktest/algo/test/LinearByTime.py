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
        # Find numQ questions later than the last question
        if lastQuestion:
            questions = QuestionBank.objects.\
                filter(companyid=self.companyId,
                       positionid=self.positionId,
                       questionid__gt=lastQuestion).limit(numQ)
        else:
            # Maybe there were no test taken for this
            # company/position by the user
            questions = QuestionBank.objects.\
                                     filter(companyid=self.companyId,
                                            positionid=self.positionId).\
                                     limit(numQ)
        # If not go back and add questions at the beginning
        if len(questions) < numQ:
            questions.extend(QuestionBank.objects.
                             filter(companyid=self.companyId,
                                    positionid=self.positionId).
                             limit(numQ-len(questions)))
        self.numQ = len(questions)
        self.questions = questions
