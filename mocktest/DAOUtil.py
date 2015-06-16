from cassandra.cqlengine.columns import TimeUUID
from cassandra.cqlengine.models import Model
from models import PositionRevLookup
from models import CompanyRevLookup
from models import CompanyPosition
from models import PositionCompany
from models import QuestionBank
from models import Users
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


def __addPositionCompany(companyId,
                         companyName,
                         positionId,
                         positionName):
    posComp = PositionCompany()
    posComp.positionid = positionId
    posComp.positionname = positionName
    posComp.companyid = companyId
    posComp.companyname = companyName
    posComp.save()


def __addPositionRevLookup(positionName,
                           positionId):
    positionLookup = PositionRevLookup()
    positionLookup.positionname = positionName
    positionLookup.positionid = positionId
    positionLookup.save()


def __addNewPosition(companyId,
                     companyName,
                     positionName):
    positionId = TimeUUID.from_datetime(datetime.now())
    __addPositionCompany(companyId,
                         companyName,
                         positionId,
                         positionName)
    __addPositionRevLookup(positionName,
                           positionId)


@cleanInput
def addCompanyPosition(companyName, positionName):
    # Check if combination exists
    isCompany, isPosition, isBoth = isPresent(companyName,
                                              positionName)
    logger.debug("Adding company " + str(companyName) +
                 " and position " + str(positionName))
    logger.debug("Existing Company: " + str(isCompany) +
                 " Existing Position: " + str(isPosition) +
                 " Existing combination: " + str(isBoth))
    if (not isBoth):
        if (not isCompany):
            # Add New Company
            compPos = CompanyPosition()
            companyId = TimeUUID.from_datetime(datetime.now())
            compPos.companyid = companyId
            compPos.companyname = companyName
            if not isPosition:
                # Add New Position
                __addNewPosition(companyId,
                                 companyName,
                                 positionName)
            else:
                # Add company to existing Position
                __addPositionCompany(companyId,
                                     companyName,
                                     getPositionId(positionName),
                                     positionName)
            compPos.positionid = getPositionId(positionName)
            compPos.positionname = positionName
            compPos.save()
            companyLookup = CompanyRevLookup()
            companyLookup.companyname = companyName
            companyLookup.companyid = companyId
            companyLookup.save()
        else:
            if not isPosition:
                # Add New Position
                __addNewPosition(getCompanyId(companyName),
                                 companyName,
                                 positionName)
            else:
                # Add company position map
                compPos = CompanyPosition()
                compPos.companyid = getCompanyId(companyName)
                compPos.positionid = getPositionId(positionName)
                compPos.companyname = companyName
                compPos.positionName = positionName
                compPos.save()


def addQuestion(companyId,
                positionId,
                question,
                answer,
                questionType=3,
                choices=[],
                input="",
                key="",
                timeToSolve=20):
    if isIdPresent(companyId, positionId):
        questionObj = QuestionBank()
        questionObj.companyid = companyId
        questionObj.positionid = positionId
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


def editQuestion(companyId,
                 positionId,
                 questionId,
                 question,
                 answer,
                 questionType=3,
                 choices=[],
                 input="",
                 key="",
                 timeToSolve=20):
    if isValidQuestionId(companyId, positionId, questionId):
        questionObj = QuestionBank.objects.get(companyid=companyId,
                                               positionid=positionId,
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


def addRawQuestion(companyId,
                   positionId,
                   question,
                   answer,
                   url,
                   questionType=3,
                   choices=[],
                   input="",
                   key="",
                   timeToSolve=20):
    if isIdPresent(companyId, positionId):
        question = QuestionBank()
        question.companyid = companyId
        question.positionid = positionId
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
                     companyId,
                     companyName,
                     positionId,
                     positionName,
                     testStartTime,
                     testEndTime,
                     totalQuestions):
    if not isScheduledTestFound(username, testId):
        scheduledTest = UserScheduledTests()
        scheduledTest.username = username
        scheduledTest.testid = testId
        scheduledTest.testname = testName
        scheduledTest.companyid = companyId
        scheduledTest.companyname = companyName
        scheduledTest.positionid = positionId
        scheduledTest.positionname = positionName
        scheduledTest.teststarttime = testStartTime
        scheduledTest.testendtime = testEndTime
        scheduledTest.totalquestions = totalQuestions
        scheduledTest.save()


def deleteScheduledTest(username, testId):
    scheduledTest = UserScheduledTests.objects.get(username=username,
                                                   testid=testId)
    if scheduledTest:
        scheduledTest.delete()


@cleanInput
def getUserRating(username):
    user = Users.objects.get(username=username)
    if user:
        return user.rating
    return None


@cleanInput
def getCompanyId(companyName):
    companyLookup = CompanyRevLookup.objects.filter(companyname=companyName)
    if companyLookup:
        return companyLookup[0].companyid
    return None


@cleanInput
def getPositionId(positionName):
    positionLookup = PositionRevLookup.objects.filter(
                        positionname=positionName)
    if positionLookup:
        return positionLookup[0].positionid
    return None


@cleanInput
def getCompanyName(companyId):
    comp = CompanyPosition.objects.filter(companyid=companyId)
    if comp:
        return comp[0].companyname
    return None


@cleanInput
def getPositionName(positionId):
    pos = PositionCompany.objects.filter(positionid=positionId)
    if pos:
        return pos[0].positionname
    return None


def isCompanyPresent(companyName):
    return isValidCompany(companyName)


def isPositionPresent(positionName):
    return isValidPosition(positionName)


def isPresent(companyName, positionName):
    isCompany = isCompanyPresent(companyName)
    isPosition = isPositionPresent(positionName)
    if isCompany and isPosition:
        companyId = getCompanyId(companyName)
        positionId = getPositionId(positionName)
        if isIdPresent(companyId, positionId):
            return (True, True, True)
        return (True, True, False)
    else:
        return (isCompany, isPosition, False)


@cleanInput
def isScheduledTestFound(username, testId):
    return __isPresentInDB(table='UserScheduledTests',
                           column=['username', 'testid'],
                           value=[username, testId])


@cleanInput
def isValidQuestionId(companyId, positionId, questionId):
    return __isPresentInDB(table='QuestionBank',
                           column=['companyid', 'positionid', 'questionid'],
                           value=[companyId, positionId, questionId])


@cleanInput
def isIdPresent(companyId, positionId):
    return __isPresentInDB(table='CompanyPosition',
                           column=['companyid', 'positionid'],
                           value=[companyId, positionId])


@cleanInput
def isValidCompany(companyName):
    return __isPresentInDB(table='CompanyRevLookup',
                           column='companyname',
                           value=companyName)


@cleanInput
def isValidPosition(positionName):
    return __isPresentInDB(table='PositionRevLookup',
                           column='positionname',
                           value=positionName)


def __isPresentInDB(*args, **kwds):
    if isinstance(kwds['column'], collections.Iterable) and not isinstance(kwds['column'], str):
        filterClause = ','.join(map(lambda cond: cond[0] + "='" + str(cond[1]) + "'",
                                    zip(kwds['column'], kwds['value'])))
        kwds['filterClause'] = filterClause
        cmd = "%(table)s.objects.filter(%(filterClause)s)" % kwds
    else:
        cmd = "%(table)s.objects.filter(%(column)s='%(value)s')" % kwds
    print cmd
    obj = eval(cmd)
    return True if obj else False
