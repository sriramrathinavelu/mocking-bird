from cassandra.cqlengine.query import DoesNotExist
from abc import ABCMeta, abstractmethod
from cassandra.cqlengine.columns import TimeUUID
from datetime import datetime
from mocktest.models import Tests
from mocktest.models import QuestionBankMedium
from mocktest.models import QuestionBankEasy
from mocktest.models import QuestionBankHard
from mocktest.models import CompanyPosition
from mocktest.models import UserPools
from mocktest.models import Constants
from mocktest import DAOUtil
from mocktest import utils
from TestExceptions import *
import random


class BaseTest(object):
    __metaclass__ = ABCMeta

    def __init__(self, username, companyName, positionName):
        self.username = username
        self.companyName = companyName
        self.positionName = positionName
        self.numQ = None
        self.questions = None
        self.startTime = None
        self.endTime = None
        self.firstQuestion = None

    @abstractmethod
    def getQuestions(self,
                     numQ=3,
                     minduration=30,
                     difficulty=[],
                     classlabel=[]):
        pass

    def getPool(self,
                difficulty=Constants.MEDIUM,
                classLabel="all",
                isQuick=False,
                isAdvanced=False):
        if not(isQuick or isAdvanced):
            isQuick = True
        try:
            UserPoolObj = UserPools.objects.get(
                            username=self.username,
                            companyname=self.companyName,
                            positionname=self.positionName,
                            difficulty=difficulty,
                            classlabel=classLabel)
            if isQuick:
                return UserPoolObj.activeqpool
            if isAdvanced:
                return UserPoolObj.activeapool
        except DoesNotExist:
            # First test for the user I guess
            # Figure out and assign a activeQPool
            numPool = CompanyPosition.objects.get(
                        companyname=self.companyName,
                        positionname=self.positionName).poolcount
            if isQuick:
                activeQPool = random.randint(1, numPool)
                activeAPool = None
            if isAdvanced:
                activeAPool = random.randint(1, numPool)
                activeQPool = None
            DAOUtil.addUserPool(
                self.username,
                self.companyName,
                self.positionName,
                difficulty,
                classLabel,
                activeQPool,
                activeAPool)
            if isQuick:
                return activeQPool
            if isAdvanced:
                return activeAPool

    def getEndTime(self):
        if not self.endTime:
            minutes = 0
            for question in self.questions:
                minutes += question.timetosolve
            return utils.fututeTime(minutes)
        else:
            return datetime.utcfromtimestamp(self.endTime)

    def getStartTime(self):
        if not self.startTime:
            return datetime.now()
        else:
            return datetime.utcfromtimestamp(self.startTime)

    def getFirstQuestion(self):
        return self.firstQuestion

    def createTest(self,
                   startTime,
                   endTime,
                   numQ=3,
                   minduration=30,
                   difficulty=[],
                   classlabel=[]):
        self.startTime = startTime
        self.endTime = endTime
        self.getQuestions(numQ,
                          minduration,
                          difficulty,
                          classlabel)
        if self.numQ == 0:
            raise NotEnoughQuestions()
        curQ = 0
        newTest = Tests()
        self.testId = TimeUUID.from_datetime(datetime.now())
        newTest.testid = self.testId
        # Static fields are filled first
        newTest.username = self.username
        self.retrorating = DAOUtil.getUserRating(self.username)
        newTest.retrorating = self.retrorating
        newTest.companyname = self.companyName
        newTest.positionname = self.positionName
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
        if isinstance(question, QuestionBankEasy):
            newTest.table = Constants.EASY
        if isinstance(question, QuestionBankMedium):
            newTest.table = Constants.MEDIUM
        if isinstance(question, QuestionBankHard):
            newTest.table = Constants.HARD
        newTest.pool = question.pool
        newTest.classlabel = question.classlabel
        newTest.question = question.question
        newTest.questiontype = question.questiontype
        newTest.givenanswer = ""
        newTest.correctanswer = question.answer
        newTest.choices = question.choices
        newTest.input = question.input
        newTest.key = question.key
        # Save the first row for now
        newTest.save()
        # Saved to retrieve the static fields later on
        self.firstQuestion = newTest
        # We just need to save remaining questions now
        # No need to worry about the static fields
        for i in range(1, self.numQ):
            question = self.questions[i]
            newTest = Tests()
            newTest.testid = self.testId
            newTest.questionnum = curQ
            curQ += 1
            if isinstance(question, QuestionBankEasy):
                newTest.table = Constants.EASY
            if isinstance(question, QuestionBankMedium):
                newTest.table = Constants.MEDIUM
            if isinstance(question, QuestionBankHard):
                newTest.table = Constants.HARD
            newTest.pool = question.pool
            newTest.classlabel = question.classlabel
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
