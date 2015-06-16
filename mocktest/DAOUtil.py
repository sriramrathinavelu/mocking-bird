from cassandra.cqlengine.query import DoesNotExist
from cassandra.cqlengine.columns import TimeUUID
from cassandra.cqlengine.models import Model
from models import CompanyPosition
from models import PositionCompany
from models import QuestionBank
from models import Users
from django.db import connections
from models import UserScheduledTests
from datetime import datetime
import collections
import logging
import uuid
import cgi

logger = logging.getLogger(__name__)


def __cleanInput(_input):
    try:
        return _input.strip()
    except:
        return _input


def cleanInput(func):
    def newFunc(*args, **kwds):
        args = map(__cleanInput, args)
        for key in kwds:
            kwds[key] = __cleanInput(kwds[key])
        return func(*args, **kwds)
    return newFunc


def getObjAsDict(obj):
    _dict = {}
    for key in obj.__dict__['_values']:
        _dict[key] = obj.__dict__['_values'][key].value
    return _dict


def __jsonReady(value, escape=False):
    if isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, uuid.UUID):
        return str(value)
    elif escape and (isinstance(value, str) or isinstance(value, unicode)):
        return cgi.escape(value)
    else:
        return value


def jsonReady(obj):
    if isinstance(obj, Model):
        _dict = dict(obj)
        for key, value in _dict.iteritems():
            _dict[key] = __jsonReady(value, True)
        return _dict
    elif isinstance(obj, collections.Iterable):
        if isinstance(obj, dict):
            for key, value in obj.iteritems():
                obj[__jsonReady(key)] = __jsonReady(value)
            return obj
        return map(__jsonReady, obj)
    else:
        return __jsonReady(obj)


def __addPositionCompany(positionName,
                         companyName):
    posComp = PositionCompany()
    posComp.positionname = positionName
    posComp.companyname = companyName
    posComp.save()


def __deletePositionCompany(positionName, companyName):
    try:
        posComp = PositionCompany.objects.get(positionname=positionName,
                                              companyname=companyName)
        posComp.delete()
    except DoesNotExist:
        pass


def __addCompanyPosition(companyName,
                         positionName):
    comPos = CompanyPosition()
    comPos.companyname = companyName
    comPos.positionname = positionName
    comPos.save()


def __deleteCompanyPosition(companyName, positionName):
    try:
        comPos = CompanyPosition.objects.get(companyname=companyName,
                                             positionname=positionName)
        comPos.delete()
    except DoesNotExist:
        pass


def deleteCompanyPosition(companyName, positionName):
    __deleteCompanyPosition(companyName, positionName)
    __deletePositionCompany(positionName, companyName)


@cleanInput
def addCompanyPosition(companyName, positionName):
    logger.debug("Adding company " + str(companyName) +
                 " and position " + str(positionName))
    try:
        if not isCompanyPositionPresent(companyName, positionName):
            __addCompanyPosition(companyName, positionName)
        if not isPositionCompanyPresent(positionName, companyName):
            __addPositionCompany(positionName, companyName)
        return True
    except Exception, e:
        logger.error("Encounter exception " + str(e))
        deleteCompanyPosition(companyName, positionName)
        return False


def addQuestion(companyName,
                positionName,
                question,
                answer,
                questionType=3,
                choices=[],
                input="",
                key="",
                timeToSolve=20):
    if isPresent(companyName, positionName):
        questionObj = QuestionBank()
        questionObj.companyname = companyName
        questionObj.positionname = positionName
        questionObj.questionid = TimeUUID.from_datetime(datetime.now())
        questionObj.questiontype = questionType
        questionObj.question = question
        questionObj.answer = answer
        questionObj.choices = choices
        questionObj.input = input
        questionObj.key = key
        questionObj.timetosolve = timeToSolve
        questionObj.save()
    else:
        raise Exception("Invalid company and position")


def editQuestion(companyName,
                 positionName,
                 questionId,
                 question,
                 answer,
                 questionType=3,
                 choices=[],
                 input="",
                 key="",
                 timeToSolve=20):
    if isValidQuestion(companyName, positionName, questionId):
        questionObj = QuestionBank.objects.get(companyname=companyName,
                                               positionname=positionName,
                                               questionid=questionId)
        questionObj.questiontype = questionType
        questionObj.question = question
        questionObj.answer = answer
        questionObj.choices = choices
        questionObj.input = input
        questionObj.key = key
        questionObj.timetosolve = timeToSolve
        questionObj.save()
    else:
        raise Exception("Invalid company and/or position and/or question")


def addRawQuestion(companyName,
                   positionName,
                   question,
                   answer,
                   url,
                   questionType=3,
                   choices=[],
                   input="",
                   key="",
                   timeToSolve=20):
    if isPresent(companyName, positionName):
        question = QuestionBank()
        question.companyname = companyName
        question.positionname = positionName
        question.questionid = TimeUUID.from_datetime(datetime.now())
        question.questiontype = questionType
        question.question = question
        question.answer = answer
        question.choices = choices
        question.input = input
        question.key = key
        question.timetosolve = timeToSolve
        question.save()
    else:
        raise Exception("Invalid company and position")


def addScheduledTest(username,
                     testId,
                     testName,
                     companyName,
                     positionName,
                     testStartTime,
                     testEndTime,
                     totalQuestions):
    if not isScheduledTestFound(username, testId):
        scheduledTest = UserScheduledTests()
        scheduledTest.username = username
        scheduledTest.testid = testId
        scheduledTest.testname = testName
        scheduledTest.companyname = companyName
        scheduledTest.positionname = positionName
        scheduledTest.teststarttime = testStartTime
        scheduledTest.testendtime = testEndTime
        scheduledTest.totalquestions = totalQuestions
        scheduledTest.save()


def deleteScheduledTest(username, testId):
    try:
        scheduledTest = UserScheduledTests.objects.get(username=username,
                                                       testid=testId)
        scheduledTest.delete()
    except DoesNotExist:
        pass


def getDistinctCompanies():
    cursor = connections["cassandra"].cursor()
    results = cursor.execute("""
        SELECT DISTINCT companyname
        FROM company_position""")
    return map(lambda x: x['companyname'], results)


@cleanInput
def getUserRating(username):
    user = Users.objects.get(username=username)
    if user:
        return user.rating
    return None


def isPresent(companyName, positionName):
    if isCompanyPositionPresent(companyName, positionName):
        if isPositionCompanyPresent(positionName, companyName):
            return True
        else:
            __addPositionCompany(positionName, companyName)
            return True
    else:
        return False


def isCompanyPresent(companyName):
    return __isPresentInDB(table='CompanyPosition',
                           column='companyname',
                           value=companyName)


def isPositionPresent(positionName):
    return __isPresentInDB(table='PositionCompany',
                           column='positionname',
                           value=positionName)


def isCompanyPositionPresent(companyName, positionName):
    return __isPresentInDB(table='CompanyPosition',
                           column=['companyname', 'positionname'],
                           value=[companyName, positionName])


def isPositionCompanyPresent(positionName, companyName):
    return __isPresentInDB(table='PositionCompany',
                           column=['positionname', 'companyname'],
                           value=[positionName, companyName])


@cleanInput
def isScheduledTestFound(username, testId):
    return __isPresentInDB(table='UserScheduledTests',
                           column=['username', 'testid'],
                           value=[username, testId])


@cleanInput
def isValidQuestion(companyName, positionName, questionId):
    return __isPresentInDB(table='QuestionBank',
                           column=['companyname',
                                   'positionname',
                                   'questionid'],
                           value=[companyName,
                                  positionName,
                                  questionId])



def __isPresentInDB(*args, **kwds):
    if isinstance(kwds['column'], collections.Iterable) and not isinstance(kwds['column'], str):
        filterClause = ','.join(map(lambda cond: cond[0] + "='" + str(cond[1]) + "'",
                                    zip(kwds['column'], kwds['value'])))
        kwds['filterClause'] = filterClause
        cmd = "%(table)s.objects.filter(%(filterClause)s).limit(1)" % kwds
    else:
        cmd = "%(table)s.objects.filter(%(column)s='%(value)s').limit(1)" % kwds
    print cmd
    obj = eval(cmd)
    return True if obj else False
