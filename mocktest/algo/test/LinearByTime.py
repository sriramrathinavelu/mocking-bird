from mocktest.models import UserQuestion
from mocktest.models import QuestionBankMedium
from mocktest.models import Constants
from mocktest.models import CompanyPosition
from mocktest import DAOUtil
from BaseTest import BaseTest


class LinearByTime(BaseTest):

    def __init__(self, *args, **kwds):
        super(LinearByTime, self).__init__(*args, **kwds)

    def __getLastQuestion(self,
                          pool,
                          difficulty=Constants.MEDIUM,
                          classlabel="all"):
        lastQuestion = UserQuestion.objects.\
                        filter(username=self.username,
                               companyname=self.companyName,
                               positionname=self.positionName,
                               pool=pool,
                               difficulty=difficulty,
                               classlabel=classlabel).limit(1)
        if len(lastQuestion) == 1:
            return lastQuestion[0].questionid
        return None

    def __getQuickQuestions(self,
                            numQ=3,
                            minduration=30,
                            difficulty=Constants.MEDIUM,
                            classLabel="all"):
        if not difficulty:
            difficulty = Constants.MEDIUM
        if not classLabel:
            classLabel = "all"
        poolsTried = 0
        maxPools = CompanyPosition.objects.get(
                        companyname=self.companyName,
                        positionname=self.positionName).poolcount
        questionsList = []
        needed = numQ
        while poolsTried <= maxPools:
            # Get the Active Quick Pool for the user
            # Find the last question asked for that user
            activeQPool = self.getPool(difficulty,
                                       classLabel,
                                       isQuick=True)
            lastQuestion = self.__getLastQuestion(activeQPool)
            # Find numQ questions later than the last question
            if lastQuestion:
                questions = QuestionBankMedium.objects.\
                    filter(companyname=self.companyName,
                           positionname=self.positionName,
                           classlabel='all',
                           pool=activeQPool,
                           questionid__gt=lastQuestion).limit(needed)
                for question in questions:
                    questionsList.append(question)
                    DAOUtil.addUserQuestion(
                        self.username,
                        self.companyName,
                        self.positionName,
                        activeQPool,
                        difficulty,
                        classLabel,
                        question.questionid
                    )
                needed -= len(questions)
                if needed > 0:
                    # User id done with the current active pool
                    # mark it used and try with the next pool
                    DAOUtil.markPoolUsed(
                        self.username,
                        self.companyName,
                        self.positionName,
                        difficulty,
                        classLabel,
                        activeQPool,
                        None)
                else:
                    # We are done here
                    break
            else:
                # Maybe there were no test taken for this
                # company/position by the user
                questions = QuestionBankMedium.objects.\
                                filter(companyname=self.companyName,
                                       positionname=self.positionName,
                                       classlabel=classLabel,
                                       pool=activeQPool).\
                                limit(needed)
                questionsList = [q for q in questions]
                for question in questionsList:
                    DAOUtil.addUserQuestion(
                        self.username,
                        self.companyName,
                        self.positionName,
                        activeQPool,
                        difficulty,
                        classLabel,
                        question.questionid
                    )
                needed -= len(questions)
                if needed > 0:
                    DAOUtil.markPoolUsed(
                        self.username,
                        self.companyName,
                        self.positionName,
                        difficulty,
                        classLabel,
                        activeQPool,
                        None)
                else:
                    break
            poolsTried += 1
        self.numQ = len(questionsList)
        self.questions = questionsList

    def __getAdvanvcedQuestions(self,
                                numQ=3,
                                minduration=30,
                                difficulty=[],
                                classLabel=[]):
        questionsList = []
        if not difficulty:
            difficulty = [Constants.MEDIUM for x in range(numQ)]
        if not classLabel:
            classLabel = ["all" for x in range(numQ)]
        for index in range(numQ):
            # Get the active pool for the combination
            activePool = self.getPool(
                difficulty=difficulty[index],
                classLabel=classLabel[index],
                isQuick=False,
                isAdvanced=True)
            # Get the last question for that combination
            lastQuestion = self.__getLastQuestion(activePool,
                                                  difficulty=difficulty[index],
                                                  classLabel=classLabel[index])
            # Get the next question for the combination
            if lastQuestion:
                question = QuestionBankMedium.objects.\
                    filter(companyname=self.companyName,
                           positionname=self.positionName,
                           classlabel='all',
                           pool=activePool,
                           questionid__gt=lastQuestion).limit(1)
            else:
                question = QuestionBankMedium.objects.\
                    filter(companyname=self.companyName,
                           positionname=self.positionName,
                           classlabel='all',
                           pool=activePool).limit(1)
            questionsList.append(question)
            # update the user-question table
            DAOUtil.addUserQuestion(
                self.username,
                self.companyName,
                self.positionName,
                activePool,
                difficulty,
                classLabel,
                question.questionid
            )

    def getQuestions(self,
                     numQ=3,
                     minduration=30,
                     difficulty=[],
                     classlabel=[]):
        if difficulty or classlabel:
            self.__getAdvanvcedQuestions(numQ,
                                         minduration,
                                         difficulty,
                                         classlabel)
        else:
            self.__getQuickQuestions(numQ,
                                     minduration,
                                     difficulty,
                                     classlabel)
