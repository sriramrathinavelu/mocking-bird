from django.contrib.auth.decorators import login_required
from cassandra.cqlengine.query import DoesNotExist
from django.shortcuts import render
from collections import OrderedDict
from models import CompanyPosition
from django.http import HttpResponse
from models import Users, Tests
from models import UserSavedTests
from models import UserCompany
from models import UserPosition
from models import UserCompanyTests
from models import UserPositionTests
from models import UserTests
from models import UserScheduledTests
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
def getUserTests(request):
    username = request.user.username
    userTests = UserTests.objects.filter(username=username)
    tests = json.dumps(map(lambda x: DAOUtil.jsonReady(x),
                           userTests))
    return HttpResponse(tests)


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
    userTests.totalmarks = testObj.totalmarks
    userTests.scoredmarks = testObj.scoredmarks
    userTests.save()
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
    state = 1
    testObj = Tests.objects.filter(testid=testId)[0]
    testObj.state = state
    testObj.save()
    DAOUtil.deleteScheduledTest(request.user.username,
                                testId)
    return HttpResponse("ok")


@login_required
def saveAnswer(request):
    testId = uuid.UUID(request.GET.get('testId'))
    currentQ = int(request.GET.get('currentQ'))
    answer = request.GET.get('answer')
    question = Tests.objects.get(testid=testId,
                                 questionnum=currentQ)
    if (question.givenanswer.strip() == "" and answer.strip() != ""):
        question.questionsanswered += 1
    if (question.givenanswer.strip() != "" and answer.strip() == ""):
        question.questionsanswered -= 1
    question.givenanswer = answer
    question.currentQ = currentQ
    question.save()
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
