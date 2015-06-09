from abc import ABCMeta, abstractmethod
from cassandra.cqlengine.columns import TimeUUID
from datetime import datetime
from mocktest.models import Tests
from mocktest import DAOUtil
from mocktest import utils


class BaseTest(object):
    __metaclass__ = ABCMeta

    def __init__(self, username, companyId, positionId):
        self.username = username
        self.companyId = companyId
        self.positionId = positionId
        self.numQ = None
        self.questions = None

    @abstractmethod
    def getQuestions(self, numQ=3):
        pass

    def getEndTime(self):
        return utils.fututeTime(self.numQ*30)

    def getStartTime(self):
        return datetime.now()

    def createTest(self,
                   startTime,
                   endTime,
                   numQ=3):
        self.getQuestions(numQ)
        curQ = 0
        newTest = Tests()
        self.testId = TimeUUID.from_datetime(datetime.now())
        newTest.testid = self.testId
        # Static fields are filled first
        newTest.username = self.username
        self.retrorating = DAOUtil.getUserRating(self.username)
        newTest.retrorating = self.retrorating
        newTest.companyid = self.companyId
        newTest.positionid = self.positionId
        newTest.companyname = DAOUtil.getCompanyName(self.companyId)
        newTest.positionname = DAOUtil.getPositionName(self.positionId)
        newTest.state = 0
        newTest.totalquestions = self.numQ
        newTest.questionsanswered = 0
        newTest.currentquestion = 0
        newTest.isevaluated = False
        newTest.totalmarks = 100
        newTest.scoredmarks = 0
        newTest.teststarttime = self.getStartTime()
        newTest.testendtime = self.getEndTime()
        newTest.userstarttime = None
        newTest.userendtime = None
        # Time for Questions
        question = self.questions[0]
        newTest.questionnum = curQ
        curQ += 1
        newTest.questionid = question.questionid
        newTest.question = question.question
        newTest.questiontype = question.questiontype
        newTest.givenanswer = ""
        newTest.correctanswer = question.answer
        newTest.choices = question.choices
        newTest.input = question.input
        newTest.key = question.key
        # Save the first row for now
        newTest.save()
        # We just need to save remaining questions now
        # No need to worry about the static fields
        for i in range(1, self.numQ):
            question = self.questions[i]
            newTest = Tests()
            newTest.testid = self.testId
            newTest.questionnum = curQ
            curQ += 1
            newTest.questionid = question.questionid
            newTest.question = question.question
            newTest.questiontype = question.questiontype
            newTest.givenanswer = ""
            newTest.correctanswer = question.answer
            newTest.choices = question.choices
            newTest.input = question.input
            newTest.key = question.key
            newTest.save()
        return self.testId
