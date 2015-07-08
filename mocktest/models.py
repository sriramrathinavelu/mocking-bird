# from django.db import models

from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from datetime import datetime

# Create your models here.


class Constants:
    NOT_BEGUN = 0
    IN_PROGRESS = 1
    COMPLETED = 2
    UPVOTE = 1
    FAVOURITE = 2
    DOWNVOTE = 3
    EASY = 4
    MEDIUM = 5
    HARD = 6
    WRONG = 4
    PARTIALLY_CORRECT = 5
    CORRECT = 6
    EASY_RATING = 1200
    MEDIUM_RATING = 1500
    HARD_RATING = 1800


class Users(Model):
    username = columns.Text(primary_key=True)
    password = columns.Text(required=True)
    firstname = columns.Text(required=True)
    lastname = columns.Text(required=True)
    email = columns.Text(required=True)
    phone = columns.Text()
    fbid = columns.Text()
    isinternal = columns.Boolean(default=False)
    mentorrequest = columns.Boolean(default=False)
    rating = columns.Integer(primary_key=True,
                             clustering_order="DESC", default=1500)
    ratingdeviation = columns.Integer(required=True, default=350)
    volatility = columns.Float(default=0.5)
    ctime = columns.DateTime(default=datetime.now)
    mtime = columns.DateTime(default=datetime.now)


class MentorRequests(Model):
    username = columns.Text(primary_key=True)
    firstname = columns.Text(required=True)
    lastname = columns.Text(required=True)
    email = columns.Text(required=True)
    phone = columns.Text()
    companyname = columns.Text()
    positionname = columns.Text()


class ModeratorVerifiedRequests(Model):
    username = columns.Text(primary_key=True)
    firstname = columns.Text(required=True)
    lastname = columns.Text(required=True)
    email = columns.Text(required=True)
    phone = columns.Text()


class MentorVerifiedRequests(Model):
    username = columns.Text(primary_key=True)
    firstname = columns.Text(required=True)
    lastname = columns.Text(required=True)
    email = columns.Text(required=True)
    phone = columns.Text()
    companyname = columns.Text()
    positionname = columns.Text()


class Moderators(Model):
    username = columns.Text(primary_key=True)
    firstname = columns.Text(required=True)
    lastname = columns.Text(required=True)
    email = columns.Text(required=True)
    phone = columns.Text()


class Mentors(Model):
    username = columns.Text(primary_key=True)
    firstname = columns.Text(required=True)
    lastname = columns.Text(required=True)
    email = columns.Text(required=True)
    phone = columns.Text()
    companyname = columns.Text()
    positionname = columns.Text()

# Below Models adopt the Wide-Row design paradigm


class Tests(Model):
    testid = columns.TimeUUID(primary_key=True)
    testname = columns.Text(static=True)
    username = columns.Text(static=True)
    retrorating = columns.Integer(static=True)  # Needs a better name
    companyname = columns.Text(static=True)
    positionname = columns.Text(static=True)
    # STATE: 0:Not Begun, 1:In progress, 2:Completed
    state = columns.Integer(static=True)
    totalquestions = columns.Integer(static=True)
    questionsanswered = columns.Integer(static=True)
    currentquestion = columns.Integer(static=True)
    isevaluated = columns.Boolean(static=True, default=False)
    pendingevaluation = columns.Boolean(static=True, default=False)
    numevaluations = columns.Integer(static=True, default=0)
    totalmarks = columns.Float(static=True)
    scoredmarks = columns.Float(static=True)
    teststarttime = columns.DateTime(static=True)
    testendtime = columns.DateTime(static=True)
    userstarttime = columns.DateTime(static=True)
    userendtime = columns.DateTime(static=True)
    # Makes sense only if isevaluated is True
    iscleared = columns.Boolean(static=True, default=False)
    ctime = columns.DateTime(default=datetime.now)
    mtime = columns.DateTime(default=datetime.now)
    questionnum = columns.Integer(primary_key=True,
                                  required=True,
                                  clustering_order="ASC")
    questionid = columns.TimeUUID(required=True)
    # Table is not always consistent and can't be relied 100%
    table = columns.Integer(default=Constants.MEDIUM)
    pool = columns.Integer(required=True)
    classlabel = columns.Text(default="all")
    question = columns.Text(required=True)
    questiontype = columns.Integer(required=True, default=3)
    givenanswer = columns.Text()
    correctanswer = columns.Text(required=True)
    choices = columns.List(columns.Text, default=[])
    input = columns.Text()
    key = columns.Text()


class UserScheduledTests(Model):
    username = columns.Text(primary_key=True)
    testid = columns.TimeUUID(primary_key=True, clustering_order="DESC")
    testname = columns.Text(required=True, default="Test " +
                            datetime.now().strftime("%c"))
    companyname = columns.Text(required=True)
    positionname = columns.Text(required=True)
    teststarttime = columns.DateTime(required=True)
    testendtime = columns.DateTime(required=True)
    totalquestions = columns.Integer(required=True)


class UserSavedTests(Model):
    username = columns.Text(primary_key=True)
    testid = columns.TimeUUID(primary_key=True, clustering_order="DESC")
    testname = columns.Text(required=True, default="Test " +
                            datetime.now().strftime("%c"))
    companyname = columns.Text(required=True)
    positionname = columns.Text(required=True)
    testdate = columns.DateTime(required=True)
    totalquestions = columns.Integer(required=True)
    questionsanswered = columns.Integer(required=True)
    isevaluated = columns.Boolean(required=True)
    totalmarks = columns.Integer(required=True)
    scoredmarks = columns.Integer(required=True)


class UserCompany(Model):
    username = columns.Text(primary_key=True)
    companyname = columns.Text(primary_key=True)


class UserCompanyTests(Model):
    username = columns.Text(partition_key=True)
    companyname = columns.Text(partition_key=True)
    positionname = columns.Text(primary_key=True, clustering_order="DESC")
    testid = columns.TimeUUID(primary_key=True, clustering_order="DESC")
    testname = columns.Text()
    testdate = columns.DateTime(required=True)
    totalquestions = columns.Integer(required=True)
    questionsanswered = columns.Integer(required=True)
    isevaluated = columns.Boolean(required=True)
    pendingevaluation = columns.Boolean(required=True)
    totalmarks = columns.Integer(required=True)
    scoredmarks = columns.Integer(required=True)
    iscleared = columns.Boolean(default=False)


class UserPosition(Model):
    username = columns.Text(primary_key=True)
    positionname = columns.Text(primary_key=True)


class UserPositionTests(Model):
    username = columns.Text(partition_key=True)
    positionname = columns.Text(partition_key=True)
    companyname = columns.Text(primary_key=True, clustering_order="DESC")
    testid = columns.TimeUUID(primary_key=True, clustering_order="DESC")
    testname = columns.Text()
    testdate = columns.DateTime(required=True)
    totalquestions = columns.Integer(required=True)
    questionsanswered = columns.Integer(required=True)
    isevaluated = columns.Boolean(required=True)
    pendingevaluation = columns.Boolean(required=True)
    totalmarks = columns.Integer(required=True)
    scoredmarks = columns.Integer(required=True)
    iscleared = columns.Boolean(default=False)


class UserTests(Model):
    username = columns.Text(primary_key=True)
    testid = columns.TimeUUID(primary_key=True, clustering_order="DESC")
    testname = columns.Text()
    companyname = columns.Text(required=True)
    positionname = columns.Text(required=True)
    testdate = columns.DateTime(required=True)
    totalquestions = columns.Integer(required=True)
    questionsanswered = columns.Integer(required=True)
    isevaluated = columns.Boolean(required=True)
    pendingevaluation = columns.Boolean(required=True)
    totalmarks = columns.Integer(required=True)
    scoredmarks = columns.Integer(required=True)
    iscleared = columns.Boolean(default=False)


class PendingEvalTests(Model):
    companyname = columns.Text(partition_key=True)
    positionname = columns.Text(partition_key=True)
    testid = columns.TimeUUID(primary_key=True)
    testdate = columns.DateTime(required=True)
    totalquestions = columns.Integer(required=True)
    questionsanswered = columns.Integer(required=True)
    teststarttime = columns.DateTime(required=True)
    testendtime = columns.DateTime(required=True)
    islocked = columns.Boolean(default=False)
    mentorname = columns.Text()
    ctime = columns.DateTime(default=datetime.now)
    mtime = columns.DateTime(default=datetime.now)


class MentorPendingEvalTests(Model):
    mentorname = columns.Text(partition_key=True)
    testid = columns.TimeUUID(primary_key=True)
    evalid = columns.TimeUUID(primary_key=True)
    companyname = columns.Text(required=True)
    positionname = columns.Text(required=True)
    testdate = columns.DateTime(required=True)
    totalquestions = columns.Integer(required=True)
    questionsanswered = columns.Integer(required=True)
    teststarttime = columns.DateTime(required=True)
    testendtime = columns.DateTime(required=True)


class MentorEvaluation(Model):
    testid = columns.TimeUUID(partition_key=True)
    evalid = columns.TimeUUID(primary_key=True)
    questionnum = columns.Integer(primary_key=True)
    result = columns.Integer(required=True)
    mentorname = columns.Text(required=True)
    mentorcomment = columns.Text()


class MentorTempEvaluation(Model):
    testid = columns.TimeUUID(partition_key=True)
    evalid = columns.TimeUUID(primary_key=True)
    questionnum = columns.Integer(primary_key=True)
    result = columns.Integer(required=True)
    mentorname = columns.Text(required=True)
    mentorcomment = columns.Text()


class UserPools(Model):
    username = columns.Text(partition_key=True)
    companyname = columns.Text(partition_key=True)
    positionname = columns.Text(partition_key=True)
    classlabel = columns.Text(primary_key=True, default="all")
    difficulty = columns.Integer(primary_key=True)
    activeqpool = columns.Integer(static=True)
    usedqpool = columns.List(columns.Integer, default=[], static=True)
    activeapool = columns.Integer()
    usedapool = columns.List(columns.Integer, default=[])


class UserQuestion(Model):
    username = columns.Text(partition_key=True)
    companyname = columns.Text(partition_key=True)
    positionname = columns.Text(partition_key=True)
    classlabel = columns.Text(primary_key=True, default="all")
    pool = columns.Integer(primary_key=True)
    difficulty = columns.Integer(primary_key=True)
    questionid = columns.TimeUUID(primary_key=True, clustering_order="DESC")


class CompanyPosition(Model):
    companyname = columns.Text(primary_key=True)
    positionname = columns.Text(primary_key=True)
    minquestions = columns.Integer(required=True, default=3)
    minduration = columns.Integer(required=True, default=30)  # Minutes
    difficulty = columns.List(columns.Integer, default=[])
    minqperpool = columns.Integer(required=True, default=50)
    maxpools = columns.Integer(required=True, default=6)
    poolincrementcount = columns.Integer(required=True, default=50)
    poolcount = columns.Integer(default=1)
    curpool = columns.Integer(default=1)


class PositionCompany(Model):
    positionname = columns.Text(primary_key=True)
    companyname = columns.Text(primary_key=True)


class MentorCompany(Model):
    username = columns.Text(primary_key=True)
    companyname = columns.Text(primary_key=True)


class MentorCompanyPosition(Model):
    username = columns.Text(partition_key=True)
    companyname = columns.Text(primary_key=True)
    positionname = columns.Text(primary_key=True)


class MentorPosition(Model):
    username = columns.Text(primary_key=True)
    positionname = columns.Text(primary_key=True)


class MentorPositionCompany(Model):
    username = columns.Text(partition_key=True)
    positionname = columns.Text(primary_key=True)
    companyname = columns.Text(primary_key=True)


class QuestionBankEasy(Model):
    companyname = columns.Text(partition_key=True)
    positionname = columns.Text(partition_key=True)
    classlabel = columns.Text(primary_key=True, default='all')
    pool = columns.Integer(primary_key=True, default=1)
    questionid = columns.TimeUUID(primary_key=True)
    questiontype = columns.Integer(required=True)
    question = columns.Text(required=True)
    answer = columns.Text(required=True)
    choices = columns.List(columns.Text, default=[])
    input = columns.Text()
    key = columns.Text()
    timetosolve = columns.Integer(default=20)
    rating = columns.Integer(default=1200)
    ratingdeviation = columns.Integer(default=Constants.EASY_RATING)
    volatility = columns.Float(default=0.5)
    reputation = columns.Integer(default=0)


class QuestionBankMedium(Model):
    companyname = columns.Text(partition_key=True)
    positionname = columns.Text(partition_key=True)
    classlabel = columns.Text(primary_key=True, default='all')
    pool = columns.Integer(primary_key=True, default=1)
    questionid = columns.TimeUUID(primary_key=True)
    questiontype = columns.Integer(required=True)
    question = columns.Text(required=True)
    answer = columns.Text(required=True)
    choices = columns.List(columns.Text, default=[])
    input = columns.Text()
    key = columns.Text()
    timetosolve = columns.Integer(default=20)
    rating = columns.Integer(default=Constants.MEDIUM_RATING)
    ratingdeviation = columns.Integer(default=350)
    volatility = columns.Float(default=0.5)
    reputation = columns.Integer(default=0)


class QuestionBankHard(Model):
    companyname = columns.Text(partition_key=True)
    positionname = columns.Text(partition_key=True)
    classlabel = columns.Text(primary_key=True, default='all')
    pool = columns.Integer(primary_key=True, default=1)
    questionid = columns.TimeUUID(primary_key=True)
    questiontype = columns.Integer(required=True)
    question = columns.Text(required=True)
    answer = columns.Text(required=True)
    choices = columns.List(columns.Text, default=[])
    input = columns.Text()
    key = columns.Text()
    timetosolve = columns.Integer(default=20)
    rating = columns.Integer(default=Constants.HARD_RATING)
    ratingdeviation = columns.Integer(default=350)
    volatility = columns.Float(default=0.5)
    reputation = columns.Integer(default=0)


class UserQuestionInteraction(Model):
    username = columns.Text(partition_key=True)
    questionid = columns.TimeUUID(partition_key=True)
    interaction = columns.List(columns.Integer, default=[])


class UserTempFavourites(Model):
    username = columns.Text(partition_key=True)
    testid = columns.TimeUUID(partition_key=True)
    companyname = columns.Text(primary_key=True)
    positionname = columns.Text(primary_key=True)
    questionid = columns.TimeUUID(primary_key=True)
    questiontype = columns.Integer(required=True)
    question = columns.Text(required=True)
    answer = columns.Text(required=True)
    choices = columns.List(columns.Text, default=[])
    input = columns.Text()
    key = columns.Text()
    timetosolve = columns.Integer(default=20)
    rating = columns.Integer(default=1200)
    reputation = columns.Integer(default=0)


class UserFavouritesCompanyHash(Model):
    username = columns.Text(primary_key=True)
    companyname = columns.Text(primary_key=True)


class UserCompanyFavourites(Model):
    username = columns.Text(partition_key=True)
    companyname = columns.Text(primary_key=True)
    positionname = columns.Text(primary_key=True)
    questionid = columns.TimeUUID(primary_key=True)
    questiontype = columns.Integer(required=True)
    question = columns.Text(required=True)
    answer = columns.Text(required=True)
    choices = columns.List(columns.Text, default=[])
    input = columns.Text()
    key = columns.Text()
    timetosolve = columns.Integer(default=20)
    rating = columns.Integer(default=1200)
    reputation = columns.Integer(default=0)


class UserFavouritesPositionHash(Model):
    username = columns.Text(primary_key=True)
    positionname = columns.Text(primary_key=True)


class UserPositionFavourites(Model):
    username = columns.Text(partition_key=True)
    positionname = columns.Text(primary_key=True)
    companyname = columns.Text(primary_key=True)
    questionid = columns.TimeUUID(primary_key=True)
    questiontype = columns.Integer(required=True)
    question = columns.Text(required=True)
    answer = columns.Text(required=True)
    choices = columns.List(columns.Text, default=[])
    input = columns.Text()
    key = columns.Text()
    timetosolve = columns.Integer(default=20)
    rating = columns.Integer(default=1200)
    reputation = columns.Integer(default=0)


class RawQuestionBank(Model):
    companyname = columns.Text(partition_key=True)
    positionname = columns.Text(partition_key=True)
    questionid = columns.TimeUUID(primary_key=True,
                                  required=True,
                                  clustering_order="DESC")
    questiontype = columns.Integer(required=True)
    url = columns.Text(required=True)
    question = columns.Text(required=True)
    answer = columns.Text(required=True)
    choices = columns.List(columns.Text, default=[])
    input = columns.Text()
    key = columns.Text()
    timetosolve = columns.Integer(default=20)

    def __str__(self):
        return self.question + "\n\n" + self.answer + "\n\n"
