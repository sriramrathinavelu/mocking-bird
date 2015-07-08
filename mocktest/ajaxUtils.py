from django.contrib.auth.decorators import login_required
from cassandra.cqlengine.query import DoesNotExist
from django.shortcuts import render
from collections import OrderedDict
from models import CompanyPosition
from django.http import HttpResponse
from algo.score.glicko2 import Player
from models import *
from datetime import datetime
from mocktest import DAOUtil
import uuid
import logging
import json

# Create your views here.

logger = logging.getLogger('mocktest.ajaxUtil')


@login_required
def getUserCompany(request):
    username = request.user.username
    userCompanies = UserCompany.objects.filter(username=username)
    companies = OrderedDict()
    companies["DEFAULT"] = "Please select a company"
    for comp in userCompanies:
        companies[comp.companyname] = comp.companyname
    return render(request,
                  'mocktest/ajaxUtil/optionsFromDict.html',
                  {'theDict': companies})


@login_required
def getUserPosition(request):
    username = request.user.username
    userPositions = UserPosition.objects.filter(username=username)
    positions = OrderedDict()
    positions["DEFAULT"] = "Please select a position"
    for pos in userPositions:
        positions[pos.positionname] = pos.positionname
    return render(request,
                  'mocktest/ajaxUtil/optionsFromDict.html',
                  {'theDict': positions})


@login_required
def getUserCompanyPosition(request):
    username = request.user.username
    companyName = request.GET['companyName']
    userCompPositions = UserCompanyTests.objects.\
        filter(username=username,
               companyname=companyName)
    positions = OrderedDict()
    positions["DEFAULT"] = "Please select a position"
    for pos in userCompPositions:
        positions[pos.positionname] = pos.positionname
    return render(request,
                  'mocktest/ajaxUtil/optionsFromDict.html',
                  {'theDict': positions})


@login_required
def getUserPositionCompany(request):
    username = request.user.username
    positionName = request.GET['positionName']
    userPosCompanies = UserPositionTests.objects.\
        filter(username=username,
               positionname=positionName)
    companies = OrderedDict()
    companies["DEFAULT"] = "Please select a company"
    for comp in userPosCompanies:
        companies[comp.companyname] = comp.companyname
    return render(request,
                  'mocktest/ajaxUtil/optionsFromDict.html',
                  {'theDict': companies})


@login_required
def getUserCompanyFavourites(request):
    username = request.user.username
    companyName = request.GET.get('companyName')
    positionName = request.GET.get('positionName')
    objects = None
    ajaxDict = {}
    ajaxDict['objects'] = []
    ajaxDict['positions'] = []
    if companyName:
        if positionName:
            objects = UserCompanyFavourites.objects.filter(
                        username=username,
                        companyname=companyName,
                        positionname=positionName)
            for obj in objects:
                ajaxDict['objects'].append(DAOUtil.jsonReady(obj))
        else:
            objects = UserCompanyFavourites.objects.filter(
                        username=username,
                        companyname=companyName)
            for obj in objects:
                ajaxDict['objects'].append(DAOUtil.jsonReady(obj))
                ajaxDict['positions'].append(
                    DAOUtil.jsonReady(obj.positionname)
                )
            ajaxDict['positions'] = list(set(ajaxDict['positions']))
    else:
        objects = UserCompanyFavourites.objects.filter(
                    username=username)
        for obj in objects:
            ajaxDict['objects'].append(DAOUtil.jsonReady(obj))
    jsonObjects = json.dumps(ajaxDict)
    return HttpResponse(jsonObjects)


@login_required
def getUserPositionFavourites(request):
    username = request.user.username
    companyName = request.GET.get('companyName')
    positionName = request.GET.get('positionName')
    objects = None
    ajaxDict = {}
    ajaxDict['objects'] = []
    ajaxDict['companies'] = []
    if positionName:
        if companyName:
            objects = UserPositionFavourites.objects.filter(
                        username=username,
                        positionname=positionName,
                        companyname=companyName)
            for obj in objects:
                ajaxDict['objects'].append(DAOUtil.jsonReady(obj))
        else:
            objects = UserPositionFavourites.objects.filter(
                        username=username,
                        positionname=positionName)
            for obj in objects:
                ajaxDict['objects'].append(DAOUtil.jsonReady(obj))
                ajaxDict['companies'].append(
                    DAOUtil.jsonReady(obj.companyname)
                )
            ajaxDict['companies'] = list(set(ajaxDict['companies']))
    else:
        objects = UserPositionFavourites.objects.filter(
                    username=username)
    jsonObjects = json.dumps(ajaxDict)
    return HttpResponse(jsonObjects)


@login_required
def getUserTests(request):
    username = request.user.username
    userTests = UserTests.objects.filter(username=username)
    tests = json.dumps(map(lambda x: DAOUtil.jsonReady(x),
                           userTests))
    return HttpResponse(tests)


@login_required
def getMentorCompanyPosition(request):
    username = request.user.username
    companyName = request.GET['companyName']
    mentorCompPositions = MentorCompanyPosition.objects.\
        filter(username=username,
               companyname=companyName)
    positions = OrderedDict()
    positions["DEFAULT"] = "Please select a position"
    for pos in mentorCompPositions:
        positions[pos.positionname] = pos.positionname
    return render(request,
                  'mocktest/ajaxUtil/optionsFromDict.html',
                  {'theDict': positions})


@login_required
def getMentorPositionCompany(request):
    username = request.user.username
    positionName = request.GET['positionName']
    mentorPosCompanies = MentorPositionCompany.objects.\
        filter(username=username,
               positionname=positionName)
    companies = OrderedDict()
    companies["DEFAULT"] = "Please select a company"
    for comp in mentorPosCompanies:
        companies[comp.companyname] = comp.companyname
    return render(request,
                  'mocktest/ajaxUtil/optionsFromDict.html',
                  {'theDict': companies})


@login_required
def getMentorTests(request):
    username = request.user.username
    companyName = request.GET.get('companyName')
    positionName = request.GET.get('positionName')
    objects = []
    if companyName:
        if positionName:
            objects = PendingEvalTests.objects.filter(
                        companyname=companyName,
                        positionname=positionName)
        else:
            positions = MentorCompanyPosition.objects.filter(
                            username=username,
                            companyname=companyName)
            for position in positions:
                objects.extend(PendingEvalTests.objects.filter(
                                companyname=companyName,
                                positionname=position.positionname))
    elif positionName:
        companies = MentorPositionCompany.objects.filter(
                        username=username,
                        positionname=positionName)
        for company in companies:
            objects.extend(PendingEvalTests.objects.filter(
                            companyname=company.companyname,
                            positionname=positionName))
    else:
        compPos = MentorCompanyPosition.objects.filter(
                    username=username)
        for obj in compPos:
            objects.extend(PendingEvalTests.objects.filter(
                                companyname=obj.companyname,
                                positionname=obj.positionname))
    objects = map(lambda x: DAOUtil.jsonReady(x),
                  filter(lambda x: not x.islocked,
                         objects))
    return HttpResponse(json.dumps(objects))


@login_required
def getUserCompanyTests(request):
    username = request.user.username
    companyName = request.GET['companyName']
    positionName = request.GET.get('positionName')
    if not positionName:
        userCompTests = UserCompanyTests.objects.\
            filter(username=username,
                   companyname=companyName)
    else:
        userCompTests = UserCompanyTests.objects.\
            filter(username=username,
                   companyname=companyName,
                   positionname=positionName)
    tests = json.dumps(map(lambda x: DAOUtil.jsonReady(x),
                           userCompTests))
    return HttpResponse(tests)


@login_required
def getUserPositionTests(request):
    username = request.user.username
    positionName = request.GET['positionName']
    companyName = request.GET.get('companyName')
    if not companyName:
        userPosTests = UserPositionTests.objects.\
            filter(username=username,
                   positionname=positionName)
    else:
        userPosTests = UserPositionTests.objects.\
            filter(username=username,
                   positionname=positionName,
                   companyname=companyName)
    tests = json.dumps(map(lambda x: DAOUtil.jsonReady(x),
                           userPosTests))
    return HttpResponse(tests)


@login_required
def getUserSavedTests(request):
    username = request.user.username
    userTests = UserSavedTests.objects.filter(username=username)
    tests = json.dumps(map(lambda x: DAOUtil.jsonReady(x),
                           userTests))
    return HttpResponse(tests)


@login_required
def getUserSchedTests(request):
    username = request.user.username
    userTests = UserScheduledTests.objects.filter(username=username)
    tests = json.dumps(map(lambda x: DAOUtil.jsonReady(x),
                           userTests))
    return HttpResponse(tests)


@login_required
def saveTest(request):
    testId = uuid.UUID(request.GET.get('testId'))
    testName = request.GET.get('testName',
                               "Test" + datetime.now().strftime("%c"))
    if not testName:
        testName = "Test" + datetime.now().strftime("%c")
    if isinstance(testName, str) and testName.strip() == "":
        testName = "Test" + datetime.now().strftime("%c")
    username = request.user.username
    testObj = Tests.objects.get(testid=testId,
                                questionnum=0)
    try:
        saveTest = UserSavedTests.objects.get(username=username,
                                              testid=testId)
        saveTest.testname = testName
    except DoesNotExist:
        saveTest = UserSavedTests()
        saveTest.username = username
        saveTest.testid = testId
        saveTest.testname = testName
        saveTest.companyname = testObj.companyname
        saveTest.positionname = testObj.positionname
    saveTest.testdate = testObj.teststarttime
    saveTest.totalquestions = testObj.totalquestions
    saveTest.questionsanswered = testObj.questionsanswered
    saveTest.isevaluated = testObj.isevaluated
    saveTest.totalmarks = testObj.totalmarks
    saveTest.scoredmarks = testObj.scoredmarks
    saveTest.save()
    return HttpResponse("ok")


@login_required
def submitTest(request):
    testId = uuid.UUID(request.GET.get('testId'))
    testName = request.GET.get('testName')
    if not testName:
        testName = None
    if isinstance(testName, str) and testName.strip() == "":
        testName = None
    testObj = Tests.objects.get(testid=testId,
                                questionnum=0)
    testObj.state = 2
    testObj.save()
    # Check if this test was saved. If so remove it
    username = request.user.username
    try:
        saveTest = UserSavedTests.objects.get(username=username,
                                              testid=testId)
        saveTest.delete()
    except DoesNotExist:
        pass
    # Record it in usercompany, userposition,
    # usercompanytests, userpositiontests and
    # usertests
    try:
        userCompanyObj = UserCompany.objects.get(username=username,
                                                 companyname=testObj.companyname)
    except DoesNotExist:
        userCompanyObj = UserCompany()
        userCompanyObj.username = username
        userCompanyObj.companyname = testObj.companyname
        userCompanyObj.save()
    try:
        userPositionObj = UserPosition.objects.\
                          get(username=username,
                              positionname=testObj.positionname)
    except DoesNotExist:
        userPositionObj = UserPosition()
        userPositionObj.username = username
        userPositionObj.positionname = testObj.positionname
        userPositionObj.save()
    userCompanyTestObj = UserCompanyTests()
    userCompanyTestObj.username = username
    userCompanyTestObj.companyname = testObj.companyname
    userCompanyTestObj.positionname = testObj.positionname
    userCompanyTestObj.testid = testId
    userCompanyTestObj.testname = testName
    userCompanyTestObj.testdate = testObj.teststarttime
    userCompanyTestObj.totalquestions = testObj.totalquestions
    userCompanyTestObj.questionsanswered = testObj.questionsanswered
    userCompanyTestObj.isevaluated = testObj.isevaluated
    userCompanyTestObj.pendingevaluation = testObj.pendingevaluation
    userCompanyTestObj.totalmarks = testObj.totalmarks
    userCompanyTestObj.scoredmarks = testObj.scoredmarks
    userCompanyTestObj.save()
    userPositionTestObj = UserPositionTests()
    userPositionTestObj.username = username
    userPositionTestObj.companyname = testObj.companyname
    userPositionTestObj.positionname = testObj.positionname
    userPositionTestObj.testid = testId
    userPositionTestObj.testname = testName
    userPositionTestObj.testdate = testObj.teststarttime
    userPositionTestObj.totalquestions = testObj.totalquestions
    userPositionTestObj.questionsanswered = testObj.questionsanswered
    userPositionTestObj.isevaluated = testObj.isevaluated
    userPositionTestObj.pendingevaluation = testObj.pendingevaluation
    userPositionTestObj.totalmarks = testObj.totalmarks
    userPositionTestObj.scoredmarks = testObj.scoredmarks
    userPositionTestObj.save()
    userTests = UserTests()
    userTests.username = username
    userTests.testid = testId
    userTests.testname = testName
    userTests.companyname = testObj.companyname
    userTests.positionname = testObj.positionname
    userTests.testdate = testObj.teststarttime
    userTests.totalquestions = testObj.totalquestions
    userTests.questionsanswered = testObj.questionsanswered
    userTests.isevaluated = testObj.isevaluated
    userTests.pendingevaluation = testObj.pendingevaluation
    userTests.totalmarks = testObj.totalmarks
    userTests.scoredmarks = testObj.scoredmarks
    userTests.save()
    DAOUtil.addUserFavourites(
        username,
        testId)
    return HttpResponse("ok")


@login_required
def exitTest(request):
    testId = uuid.UUID(request.GET.get('testId'))
    testObjs = Tests.objects.filter(testid=testId)
    # Check if this test was saved. If so remove it
    username = request.user.username
    try:
        saveTest = UserSavedTests.objects.get(username=username,
                                              testid=testId)
        saveTest.delete()
    except DoesNotExist:
        pass
    for testObj in testObjs:
        testObj.delete()
    return HttpResponse("ok")


@login_required
def notifyTestStart(request):
    testId = uuid.UUID(request.GET.get('testId'))
    testObj = Tests.objects.filter(testid=testId)[0]
    testObj.state = Constants.IN_PROGRESS
    testObj.save()
    DAOUtil.deleteScheduledTest(request.user.username,
                                testId)
    return HttpResponse("ok")


@login_required
def saveAnswer(request):
    testId = uuid.UUID(request.GET.get('testId'))
    currentQ = int(request.GET.get('currentQ'))
    answer = request.GET.get('answer')
    oprn = request.GET.get('oprn')
    logger.debug("Answer: " + str(answer))
    question = Tests.objects.get(testid=testId,
                                 questionnum=currentQ)
    if (question.givenanswer.strip() == "" and answer.strip() != ""):
        question.questionsanswered += 1
    if (question.givenanswer.strip() != "" and answer.strip() == ""):
        question.questionsanswered -= 1
    question.givenanswer = answer
    if oprn == 'next':
        currentQ += 1
    elif oprn == 'prev':
        currentQ -= 1
    question.currentquestion = currentQ
    question.save()
    return HttpResponse("ok")


@login_required
def evaluateTest(request):
    testId = uuid.UUID(request.GET.get('testId'))
    testObj = Tests.objects.filter(testid=testId)[0]
    pendingEvalTests = PendingEvalTests()
    pendingEvalTests.companyname = testObj.companyname
    pendingEvalTests.positionname = testObj.positionname
    pendingEvalTests.testid = testId
    pendingEvalTests.testdate = testObj.teststarttime
    pendingEvalTests.totalquestions = testObj.totalquestions
    pendingEvalTests.questionsanswered = testObj.questionsanswered
    pendingEvalTests.teststarttime = testObj.teststarttime
    pendingEvalTests.testendtime = testObj.testendtime
    pendingEvalTests.save()
    testObj.pendingevaluation = True
    testObj.save()
    try:
        userCompTest = UserCompanyTests.objects.get(
            username=request.user.username,
            companyname=testObj.companyname,
            positionname=testObj.positionname,
            testid=testId)
        userCompTest.pendingevaluation = True
        userCompTest.save()
    except DoesNotExist:
        pass
    try:
        userPosTest = UserPositionTests.objects.get(
            username=request.user.username,
            positionname=testObj.positionname,
            companyname=testObj.companyname,
            testid=testId)
        userPosTest.pendingevaluation = True
        userPosTest.save()
    except DoesNotExist:
        pass
    try:
        userTest = UserTests.objects.get(
            username=request.user.username,
            testid=testId)
        userTest.pendingevaluation = True
        userTest.save()
    except DoesNotExist:
        pass
    return HttpResponse("ok")


@login_required
def saveComment(request):
    testId = uuid.UUID(request.GET.get('testId'))
    evalId = uuid.UUID(request.GET.get('evalId'))
    currentQ = int(request.GET.get('currentQ'))
    totalQuestions = int(request.GET.get('totalQuestions'))
    comment = request.GET.get('comment')
    result = request.GET.get('result')
    try:
        mentorEval = MentorTempEvaluation.objects.get(
                        testid=testId,
                        evalid=evalId,
                        questionnum=currentQ)
    except DoesNotExist:
        mentorEval = MentorTempEvaluation()
        mentorEval.testid = testId
        mentorEval.evalid = evalId
        mentorEval.questionnum = currentQ
    mentorEval.mentorname = request.user.username
    mentorEval.mentorcomment = comment
    mentorEval.result = result
    mentorEval.save()
    # Check if all answers are evaluated
    numEntries = MentorTempEvaluation.objects.filter(
        testid=testId,
        evalid=evalId).count()
    if numEntries == totalQuestions:
        return HttpResponse("done")
    return HttpResponse("ok")


@login_required
def cancelEvaluation(request):
    testId = uuid.UUID(request.GET.get('testId'))
    evalId = uuid.UUID(request.GET.get('evalId'))
    companyName = request.GET.get('companyName')
    positionName = request.GET.get('positionName')
    mentorEvals = MentorTempEvaluation.objects.filter(
        testid=testId,
        evalid=evalId)
    for mEval in mentorEvals:
        mEval.delete()
    pendingEvalTest = PendingEvalTests.get(
                        companyname=companyName,
                        positionname=positionName,
                        testid=testId)
    pendingEvalTest.islocked = False
    pendingEvalTest.save()
    mentorPendingEvalTest = MentorPendingEvalTests.objects.get(
        mentorname=request.user.username,
        testid=testId,
        evalid=evalId)
    mentorPendingEvalTest.delete()
    return HttpResponse("ok")


@login_required
def saveEvaluationResult(request):
    testId = uuid.UUID(request.GET.get('testId'))
    evalId = uuid.UUID(request.GET.get('evalId'))
    result = request.GET['result']
    question = Tests.objects.get(testid=testId,
                                 questionnum=0)
    question.isevaluated = True
    question.iscleared = result == "pass"
    question.numevaluations += 1
    question.save()
    companyName = question.companyname
    positionName = question.positionname
    username = question.username
    userTest = UserTests.get(
                username=username,
                testid=testId)
    userTest.isevaluated = True
    userTest.pendingevaluation = False
    userTest.iscleared = result == "pass"
    userTest.save()
    userCompTest = UserCompanyTests.get(
                    username=username,
                    companyname=companyName,
                    positionname=positionName,
                    testid=testId)
    userCompTest.isevaluated = True
    userCompTest.pendingevaluation = False
    userCompTest.iscleared = result == "pass"
    userCompTest.save()
    userPosTest = UserPositionTests.get(
                    username=username,
                    positionname=positionName,
                    companyname=companyName,
                    testid=testId)
    userPosTest.isevaluated = True
    userPosTest.pendingevaluation = False
    userPosTest.iscleared = result == "pass"
    userPosTest.save()
    try:
        mentorPendingEvalTest = MentorPendingEvalTests.objects.get(
            mentorname=request.user.username,
            testid=testId,
            evalid=evalId)
        mentorPendingEvalTest.delete()
    except DoesNotExist:
        pass
    try:
        pendingEvalTest = PendingEvalTests.get(
                            companyname=companyName,
                            positionname=positionName,
                            testid=testId)
        pendingEvalTest.delete()
    except DoesNotExist:
        pass
    evals = MentorTempEvaluation.objects.filter(
                testid=testId,
                evalid=evalId)
    for _eval in evals:
        mentorEval = MentorEvaluation()
        mentorEval.testid = _eval.testid
        mentorEval.evalid = _eval.evalid
        mentorEval.questionnum = _eval.questionnum
        mentorEval.result = _eval.result
        mentorEval.mentorname = _eval.mentorname
        mentorEval.mentorcomment = _eval.mentorcomment
        mentorEval.save()
        _eval.delete()
    return HttpResponse("ok")


def getPositions(request):
    companyName = request.GET.get('companyName', None)
    positionsDB = CompanyPosition.objects.filter(companyname=companyName)
    positions = OrderedDict()
    positions["DEFAULT"] = "Search for a position"
    for position in positionsDB:
        positions[position.positionname] = position.positionname
    return render(request,
                  'mocktest/ajaxUtil/optionsFromDict.html',
                  {'theDict': positions})


def isUsernameValid(request):
    if not request.GET.get("username"):
        return HttpResponse("no")
    else:
        username = request.GET.get("username")
        user = Users.all().filter(username=username)
        if (user):
            return HttpResponse("no")
        return HttpResponse("ok")


@login_required
def mentorRequest(request):
    username = request.user.username
    userObj = Users.objects.get(username=username)
    DAOUtil.addMentorRequest(userObj)
    DAOUtil.updateAuthUserGroup(username, 'MentorsWaitingList')
    return HttpResponse("ok")


@login_required
def updateUserQuestionInteraction(request):
    username = request.user.username
    questionId = request.GET.get("questionId")
    companyName = request.GET.get("companyName")
    positionName = request.GET.get("positionName")
    pool = request.GET.get("pool")
    classLabel = request.GET.get("classlabel")
    testId = request.GET.get('testId')
    difficultySet = set([Constants.EASY, Constants.MEDIUM, Constants.HARD])
    try:
        interaction = int(request.GET.get("interaction"))
    except ValueError, e:
        logger.error("Value Error " + str(e))
        return HttpResponse("Error")
    userQuestionInteraction = None
    try:
        userQuestionInteraction = UserQuestionInteraction.objects.\
            get(username=username,
                questionid=questionId)
        dbList = userQuestionInteraction.interaction
        if interaction not in dbList:
            if interaction in difficultySet:
                dbList = [x for x in dbList if x not in difficultySet]
            dbList.append(interaction)
        else:
            return HttpResponse("ok")
        userQuestionInteraction.interaction = dbList
        userQuestionInteraction.save()
    except DoesNotExist, e:
        dbList = [interaction]
        userQuestionInteraction = UserQuestionInteraction()
        userQuestionInteraction.username = username
        userQuestionInteraction.questionid = questionId
        userQuestionInteraction.interaction = dbList
        userQuestionInteraction.save()
    if interaction == Constants.UPVOTE:
        # Increase Reputation By One
        question = QuestionBankMedium.objects.get(
                    companyname=companyName,
                    positionname=positionName,
                    classlabel=classLabel,
                    pool=pool,
                    questionid=questionId)
        question.reputation += 1
        question.save()
    elif interaction == Constants.FAVOURITE:
        try:
            UserCompanyFavourites.objects.get(
                        username=username,
                        companyname=companyName,
                        positionname=positionName,
                        questionid=questionId)
        except DoesNotExist, e:
            question = QuestionBankMedium.objects.get(
                    companyname=companyName,
                    positionname=positionName,
                    classlabel=classLabel,
                    pool=pool,
                    questionid=questionId)
            DAOUtil.addUserTempFavourites(username,
                                          testId,
                                          companyName,
                                          positionName,
                                          questionId,
                                          question.questiontype,
                                          question.question,
                                          question.answer,
                                          question.choices,
                                          question.input,
                                          question.key,
                                          question.timetosolve,
                                          question.rating,
                                          question.reputation)
    elif interaction == Constants.DOWNVOTE:
        question = QuestionBankMedium.objects.get(
                    companyname=companyName,
                    positionname=positionName,
                    classlabel=classLabel,
                    pool=pool,
                    questionid=questionId)
        question.reputation -= 1
        if question.reputation < -50:
            threshold = Users.objects.all().count()*(-0.2)
            if question.reputation < threshold:
                logger.info("Deleting question " + str(questionId))
                question.delete()
        question.save()
    elif interaction >= Constants.EASY:
        user = Users.objects.get(username=username)
        userRating = user.rating
        userRatingDeviation = user.ratingdeviation
        question = QuestionBankMedium.objects.get(
                    companyname=companyName,
                    positionname=positionName,
                    classlabel=classLabel,
                    pool=pool,
                    questionid=questionId)
        problem = Player(question.rating,
                         question.ratingdeviation,
                         question.volatility)
        problem.update_player([userRating],
                              [userRatingDeviation],
                              [(interaction-Constants.EASY)/2.0])
        question.rating = problem.rating
        question.ratingdeviation = problem.rd
        question.volatility = problem.vol
        question.save()
    return HttpResponse("add")
