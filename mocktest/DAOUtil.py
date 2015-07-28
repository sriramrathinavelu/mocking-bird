from cassandra.cqlengine.query import DoesNotExist
from cassandra.cqlengine.columns import TimeUUID
from cassandra.cqlengine.models import Model
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from models import *
from mailer import *
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


def jsonReady(obj, extraparams={}, escape=False):
    if isinstance(obj, Model):
        _dict = dict(obj)
        for key, value in _dict.iteritems():
            _dict[key] = jsonReady(value, escape=True)
        for key, value in extraparams.iteritems():
            _dict[__jsonReady(key)] = jsonReady(value)
        return _dict
    elif isinstance(obj, collections.Iterable):
        if isinstance(obj, dict):
            for key, value in obj.iteritems():
                obj[__jsonReady(key)] = jsonReady(value)
            for key, value in extraparams.iteritems():
                obj[__jsonReady(key)] = jsonReady(value)
            return obj
        if isinstance(obj, list) or isinstance(obj, tuple):
            return map(jsonReady, obj)
        if isinstance(obj, str) or isinstance(obj, unicode):
            return __jsonReady(obj)
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
                         positionName,
                         minQuestions,
                         minDuration,
                         minQPerPool,
                         maxPools,
                         poolIncrementCount):
    comPos = CompanyPosition()
    comPos.companyname = companyName
    comPos.positionname = positionName
    comPos.minquestions = minQuestions
    comPos.minduration = minDuration
    comPos.minqperpool = minQPerPool
    comPos.maxpools = maxPools
    if poolIncrementCount > 0:
        comPos.poolincrementcount = poolIncrementCount
    else:
        comPos.poolincrementcount = 25
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
def addCompanyPosition(companyName,
                       positionName,
                       minQuestions,
                       minDuration,
                       minQPerPool,
                       maxPools,
                       poolIncrementCount):
    logger.debug("Adding company " + str(companyName) +
                 " and position " + str(positionName))
    try:
        if not isCompanyPositionPresent(companyName, positionName):
            __addCompanyPosition(companyName,
                                 positionName,
                                 minQuestions,
                                 minDuration,
                                 minQPerPool,
                                 maxPools,
                                 poolIncrementCount)
        if not isPositionCompanyPresent(positionName, companyName):
            __addPositionCompany(positionName, companyName)
        return True
    except Exception, e:
        logger.error("Encounter exception " + str(e))
        deleteCompanyPosition(companyName, positionName)
        return False


@cleanInput
def editCompanyPosition(companyName,
                        positionName,
                        minQuestions,
                        minDuration,
                        minQPerPool,
                        maxPools,
                        poolIncrementCount,
                        poolCount,
                        currentPool):
    logger.debug("Editing company " + str(companyName) +
                 " and position " + str(positionName))
    try:
        compPosObj = CompanyPosition.objects.get(
            companyname=companyName,
            positionname=positionName)
        compPosObj.minquestions = minQuestions
        compPosObj.minduration = minDuration
        compPosObj.minqperpool = minQPerPool
        compPosObj.maxpools = maxPools
        compPosObj.poolincrementcount = poolIncrementCount
        compPosObj.poolcount = poolCount
        compPosObj.curpool = currentPool
        compPosObj.save()
        return True
    except Exception, e:
        logger.error("Encounter exception " + str(e))
        return False


def addUserQuestion(username,
                    companyName,
                    positionName,
                    pool,
                    difficulty,
                    classLabel,
                    questionId):
    userQuestionObj = UserQuestion()
    userQuestionObj.username = username
    userQuestionObj.companyname = companyName
    userQuestionObj.positionname = positionName
    userQuestionObj.pool = pool
    userQuestionObj.difficulty = difficulty
    userQuestionObj.classlabel = classLabel
    userQuestionObj.questionid = questionId
    userQuestionObj.save()


def addUserTempFavourites(username,
                          testId,
                          companyName,
                          positionName,
                          questionId,
                          questionType,
                          question,
                          answer,
                          choices,
                          input,
                          key,
                          timeToSolve,
                          rating,
                          reputation):
    userTempFav = UserTempFavourites()
    userTempFav.username = username
    userTempFav.testid = testId
    userTempFav.companyname = companyName
    userTempFav.positionname = positionName
    userTempFav.questionid = questionId
    userTempFav.questiontype = questionType
    userTempFav.question = question
    userTempFav.answer = answer
    userTempFav.choices = choices
    userTempFav.input = input
    userTempFav.key = key
    userTempFav.timetosolve = timeToSolve
    userTempFav.rating = rating
    userTempFav.reputation = reputation
    userTempFav.save()


def addUserNotification(username,
                        notificationType,
                        pageName,
                        content):
    # Optional add validation on page name (if needed)
    if notificationType in (Constants.BUBBLE_NOTIFICATION,
                            Constants.POPUP_NOTIFICATION):
        try:
            userNotification = UserNotifications.objects.get(
                    username=username,
                    pagename=pageName,
                    notificationtype=notificationType)
            if notificationType == Constants.BUBBLE_NOTIFICATION:
                userNotification.content = str(int(userNotification.content) +
                                               int(content))
            else:
                userNotification.content = userNotification.content + \
                                           "\\n\\n" + \
                                           content
        except DoesNotExist:
            userNotification = UserNotifications()
            userNotification.username = username
            userNotification.notificationtype = notificationType
            userNotification.pagename = pageName
            userNotification.notificationid = TimeUUID.from_datetime(
                datetime.now()
            )
            userNotification.content = content
        userNotification.save()
    elif notificationType == Constants.WIZARD_NOTIFICATION and \
            isinstance(content, list):
        for msg in content:
            userNotification = UserNotifications()
            userNotification.username = username
            userNotification.notificationtype = notificationType
            userNotification.pagename = pageName
            userNotification.notificationid = TimeUUID.from_datetime(
                datetime.now()
            )
            userNotification.content = msg
            userNotification.save()
    else:
        raise Exception("Invalid notification type")


def addUserFavourites(username, testId):
    favs = UserTempFavourites.objects.filter(
            username=username,
            testid=testId)
    if len(favs) == 0:
        return
    companyName = favs[0].companyname
    positionName = favs[0].positionname
    try:
        UserFavouritesCompanyHash.objects.get(
            username=username,
            companyname=companyName)
    except DoesNotExist:
        userFavCompHash = UserFavouritesCompanyHash()
        userFavCompHash.username = username
        userFavCompHash.companyname = companyName
        userFavCompHash.save()
    try:
        UserFavouritesPositionHash.objects.get(
            username=username,
            positionname=positionName)
    except DoesNotExist:
        userFavPosHash = UserFavouritesPositionHash()
        userFavPosHash.username = username
        userFavPosHash.positionname = positionName
        userFavPosHash.save()
    for fav in favs:
        userComFav = UserCompanyFavourites()
        userComFav.username = username
        userComFav.companyname = companyName
        userComFav.positionname = positionName
        userComFav.questionid = fav.questionid
        userComFav.questiontype = fav.questiontype
        userComFav.question = fav.question
        userComFav.answer = fav.answer
        userComFav.choices = fav.choices
        userComFav.input = fav.input
        userComFav.key = fav.key
        userComFav.timetosolve = fav.timetosolve
        userComFav.rating = fav.rating
        userComFav.reputation = fav.reputation
        userPosFav = UserPositionFavourites()
        userPosFav.username = username
        userPosFav.companyname = companyName
        userPosFav.positionname = positionName
        userPosFav.questionid = fav.questionid
        userPosFav.questiontype = fav.questiontype
        userPosFav.question = fav.question
        userPosFav.answer = fav.answer
        userPosFav.choices = fav.choices
        userPosFav.input = fav.input
        userPosFav.key = fav.key
        userPosFav.timetosolve = fav.timetosolve
        userPosFav.rating = fav.rating
        userPosFav.reputation = fav.reputation
        userComFav.save()
        userPosFav.save()


def __unused_addUserFavourites(username,
                               companyName,
                               positionName,
                               questionId,
                               questionType,
                               question,
                               answer,
                               choices,
                               input,
                               key,
                               timeToSolve,
                               rating,
                               reputation):
    try:
        UserFavouritesCompanyHash.objects.get(
            username=username,
            companyname=companyName)
    except DoesNotExist:
        userFavCompHash = UserFavouritesCompanyHash()
        userFavCompHash.username = username
        userFavCompHash.companyname = companyName
        userFavCompHash.save()
    userComFav = UserCompanyFavourites()
    userComFav.username = username
    userComFav.companyname = companyName
    userComFav.positionname = positionName
    userComFav.questionid = questionId
    userComFav.questiontype = questionType
    userComFav.question = question
    userComFav.answer = answer
    userComFav.choices = choices
    userComFav.input = input
    userComFav.key = key
    userComFav.timetosolve = timeToSolve
    userComFav.rating = rating
    userComFav.reputation = reputation
    try:
        UserFavouritesPositionHash.objects.get(
            username=username,
            positionname=positionName)
    except DoesNotExist:
        userFavPosHash = UserFavouritesPositionHash()
        userFavPosHash.username = username
        userFavPosHash.positionname = positionName
        userFavPosHash.save()
    userPosFav = UserPositionFavourites()
    userPosFav.username = username
    userPosFav.companyname = companyName
    userPosFav.positionname = positionName
    userPosFav.questionid = questionId
    userPosFav.questiontype = questionType
    userPosFav.question = question
    userPosFav.answer = answer
    userPosFav.choices = choices
    userPosFav.input = input
    userPosFav.key = key
    userPosFav.timetosolve = timeToSolve
    userPosFav.rating = rating
    userPosFav.reputation = reputation
    userComFav.save()
    userPosFav.save()


def addUserPool(username,
                companyName,
                positionName,
                difficulty,
                classLabel,
                activeQPool,
                activeAPool):
    newUserPool = UserPools()
    newUserPool.username = username
    newUserPool.companyname = companyName
    newUserPool.positionname = positionName
    newUserPool.difficulty = difficulty
    newUserPool.classlabel = classLabel
    newUserPool.activeqpool = activeQPool
    newUserPool.activeapool = activeAPool
    newUserPool.save()


def markPoolUsed(username,
                 companyName,
                 positionName,
                 difficulty,
                 classLabel,
                 usedQPool,
                 usedAPool):
    obj = UserPools.objects.get(
            username=username,
            companyname=companyName,
            positionname=positionName,
            difficulty=difficulty,
            classlabel=classLabel
          )
    maxPools = CompanyPosition.objects.get(
            companyname=companyName,
            positionname=positionName
        ).poolcount
    if usedQPool:
        obj.activeqpool = (usedQPool % maxPools) + 1
        obj.usedqpool.append(usedQPool)
    if usedAPool:
        obj.activeapool = (usedAPool % maxPools) + 1
        obj.usedapool.append(usedAPool)
    obj.save()


def getQuestionClass(difficulty=Constants.MEDIUM):
    questionClass = None
    if difficulty == Constants.MEDIUM:
        questionClass = QuestionBankMedium
    elif difficulty == Constants.EASY:
        questionClass = QuestionBankEasy
    else:
        questionClass = QuestionBankHard
    return questionClass


def getActivePool(companyName,
                  positionName,
                  difficulty=Constants.MEDIUM,
                  classLabel='all'):
    questionClass = getQuestionClass(difficulty)
    # Get the active pool from the CompanyPosition table
    compPosObj = CompanyPosition.objects.get(
        companyname=companyName,
        positionname=positionName)
    # Get count of questions in the active pool
    count = questionClass.objects.filter(
        companyname=companyName,
        positionname=positionName,
        classlabel=classLabel,
        pool=compPosObj.curpool).count()
    if count + 1 <= compPosObj.minqperpool:
        return compPosObj.curpool
    else:
        while True:
            # Try next pool
            compPosObj.curpool += 1
            if compPosObj.curpool > compPosObj.maxpools:
                # All pools are filled. Bump up the count of each pool
                compPosObj.curpool = 1
                compPosObj.minqperpool += compPosObj.poolincrementcount
            count = questionClass.objects.filter(
                companyname=companyName,
                positionname=positionName,
                classlabel=classLabel,
                pool=compPosObj.curpool).count()
            if count == 0:
                # Using the pool for the very first time
                # Increment poolcount
                compPosObj.poolcount += 1
            if count + 1 <= compPosObj.minqperpool:
                compPosObj.save()
                return compPosObj.curpool


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
        activePool = getActivePool(
            companyName=companyName,
            positionName=positionName,
            difficulty=Constants.MEDIUM,
            classLabel='all')
        questionObj = QuestionBankMedium()
        questionObj.companyname = companyName
        questionObj.positionname = positionName
        questionObj.classLabel = 'all'
        questionObj.pool = activePool
        questionObj.questionid = TimeUUID.from_datetime(datetime.now())
        questionObj.questiontype = questionType
        questionObj.question = question
        questionObj.answer = answer
        questionObj.choices = choices
        questionObj.input = input
        questionObj.key = key
        questionObj.timetosolve = timeToSolve
        questionObj.save()
        return questionObj
    else:
        raise Exception("Invalid company and position")


def updateQuestionDifficulty(questionObj):
    if isinstance(questionObj, QuestionBankMedium):
        if questionObj.rating <= 1200 and questionObj.ratingdeviation < 100:
            # Move it to the easy table
            questionObjEasy = QuestionBankEasy()
            for item in questionObj.items():
                questionObjEasy.__setattr__(
                    item[0],
                    item[1]
                )
                questionObjEasy.save()
                questionObj.delete()
        elif questionObj.rating >= 1800 and questionObj.ratingdeviation < 100:
            # Move it to the hard table
            questionObjHard = QuestionBankHard()
            for item in questionObj.items():
                questionObjHard.__setattr__(
                    item[0],
                    item[1]
                )
                questionObjHard.save()
                questionObj.delete()
    elif isinstance(questionObj, QuestionBankEasy):
        if questionObj.rating >= 1500 and questionObj.ratingdeviation < 100:
            # Move it to the medium table
            questionObjMedium = QuestionBankMedium()
            for item in questionObj.items():
                questionObjMedium.__setattr__(
                    item[0],
                    item[1]
                )
                questionObjMedium.save()
                questionObj.delete()
    else:
        if questionObj.rating <= 1500 and questionObj.ratingdeviation < 100:
            # Move it to the medium table
            questionObjMedium = QuestionBankMedium()
            for item in questionObj.items():
                questionObjMedium.__setattr__(
                    item[0],
                    item[1]
                )
                questionObjMedium.save()
                questionObj.delete()


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
        questionObj = QuestionBankMedium.objects.get(companyname=companyName,
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
        return questionObj
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
        question = RawQuestionBank()
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


def __addAuthUser(username, isMentor, isInternal=False):
    authUser, created = User.objects.get_or_create(
                            username=username,
                            password='mockingsite'
                        )
    authUser.save()
    try:
        userWL = Group.objects.get(name='UsersWaitingList')
    except Group.DoesNotExist:
        userWL = Group(name='UsersWaitingList')
        userWL.save()
    authUser.groups.add(userWL)
    if isInternal:
        try:
            moderatorWL = Group.objects.get(name='ModeratorsWaitingList')
        except Group.DoesNotExist:
            moderatorWL = Group(name='ModeratorsWaitingList')
            moderatorWL.save()
        authUser.groups.add(moderatorWL)
    # Hack to make it work in openshift
    authUser.last_login = datetime.now()
    if isMentor:
        try:
            mentorWL = Group.objects.get(name='MentorsWaitingList')
        except Group.DoesNotExist:
            mentorWL = Group(name='MentorsWaitingList')
            mentorWL.save()
        authUser.groups.add(mentorWL)
    authUser.save()


def updateAuthUserGroup(username, grpName):
    authUser = User.objects.get(username=username)
    try:
        newGrp = Group.objects.get(name=grpName)
    except Group.DoesNotExist:
        newGrp = Group(name=grpName)
        newGrp.save()
    authUser.groups.add(newGrp)


def addMentorRequest(userObject):
    mentorReq = MentorRequests()
    mentorReq.username = userObject.username
    mentorReq.firstname = userObject.firstname
    mentorReq.lastname = userObject.lastname
    mentorReq.email = userObject.email
    mentorReq.phone = userObject.phone
    mentorReq.save()


def addUser(username,
            password,
            fbid,
            firstName,
            lastName,
            email,
            phone,
            timezone,
            isMentor=False,
            isInternal=False):
    newUser = Users()
    newUser.username = username
    password = password or fbid
    newUser.password = password
    newUser.firstname = firstName
    newUser.lastname = lastName
    if isMentor:
        newUser.mentorrequest = True
    if isInternal:
        newUser.isinternal = True
    newUser.email = email
    phonenumber = phone
    if (phonenumber and phonenumber.startswith("Phone")):
        phonenumber = None
    newUser.phone = phonenumber
    newUser.fbid = fbid
    newUser.ianatimezone = timezone
    newUser.save()
    emailCode = PostOffice.NEW_USER
    if isMentor:
        addMentorRequest(newUser)
        emailCode = PostOffice.NEW_USER_MENTOR
    if isInternal:
        emailCode = PostOffice.NEW_MODERATOR
    __addAuthUser(username, isMentor, isInternal)
    sendMail(email, emailCode, {
                'username': username,
                'verificationURL':
                "http://crackit.com:8000/admin/verification.html?" +
                "username=%s" % (username)
        })
    addUserNotification(
        username=username,
        notificationType=Constants.WIZARD_NOTIFICATION,
        pageName="home",
        content=[
            "This is the first time you login. Please let us walk through",
            "Please select a company or All company to get questions " +
            " from all companies",
            "Please then select a position you are applying",
            "Click \"Quick Test\" to launch a test immediately or choose " +
            " advanced test and schedule a test with advanced settings",
            "Enjoy your test\\n\\n We wish you all the best"
        ]
    )
    return True


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
    companies = map(lambda x: x['companyname'], results)
    cursor.close()
    return companies


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
