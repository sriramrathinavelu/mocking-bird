from django.contrib.auth.decorators import login_required
from cassandra.cqlengine.query import DoesNotExist
from models import CompanyRevLookup
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
        companies[comp.companyid] = comp.companyname
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
        positions[pos.positionid] = pos.positionname
    return render(request,
                  'mocktest/ajaxUtil/optionsFromDict.html',
                  {'theDict': positions})


@login_required
def getUserCompanyPosition(request):
    username = request.user.username
    companyId = request.GET['companyId']
    userCompPositions = UserCompanyTests.objects.filter(username=username,
                                                        companyid=companyId)
    positions = OrderedDict()
    positions["DEFAULT"] = "Please select a position"
    for pos in userCompPositions:
        positions[pos.positionid] = pos.positionname
    return render(request,
                  'mocktest/ajaxUtil/optionsFromDict.html',
                  {'theDict': positions})


@login_required
def getUserPositionCompany(request):
    username = request.user.username
    positionId = request.GET['positionId']
    userPosCompanies = UserPositionTests.objects.filter(username=username,
                                                        positionid=positionId)
    companies = OrderedDict()
    companies["DEFAULT"] = "Please select a company"
    for comp in userPosCompanies:
        companies[comp.companyid] = comp.companyname
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
    companyId = request.GET['companyId']
    positionId = request.GET.get('positionId')
    if not positionId:
        userCompTests = UserCompanyTests.objects.filter(username=username,
                                                        companyid=companyId)
    else:
        userCompTests = UserCompanyTests.objects.filter(username=username,
                                                        companyid=companyId,
                                                        positionid=positionId)
    tests = json.dumps(map(lambda x: DAOUtil.jsonReady(x),
                           userCompTests))
    return HttpResponse(tests)


@login_required
def getUserPositionTests(request):
    username = request.user.username
    positionId = request.GET['positionId']
    companyId = request.GET.get('companyId')
    if not companyId:
        userPosTests = UserPositionTests.objects.filter(username=username,
                                                        positionid=positionId)
    else:
        userPosTests = UserPositionTests.objects.filter(username=username,
                                                        positionid=positionId,
                                                        companyid=companyId)
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
        saveTest.companyid = testObj.companyid
        saveTest.companyname = testObj.companyname
        saveTest.positionid = testObj.positionid
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
                                                 companyid=testObj.companyid)
    except DoesNotExist:
        userCompanyObj = UserCompany()
        userCompanyObj.username = username
        userCompanyObj.companyid = testObj.companyid
        userCompanyObj.companyname = testObj.companyname
        userCompanyObj.save()
    try:
        userPositionObj = UserPosition.objects.\
                          get(username=username,
                              positionid=testObj.positionid)
    except DoesNotExist:
        userPositionObj = UserPosition()
        userPositionObj.username = username
        userPositionObj.positionid = testObj.positionid
        userPositionObj.positionname = testObj.positionname
        userPositionObj.save()
    userCompanyTestObj = UserCompanyTests()
    userCompanyTestObj.username = username
    userCompanyTestObj.companyid = testObj.companyid
    userCompanyTestObj.companyname = testObj.companyname
    userCompanyTestObj.positionid = testObj.positionid
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
    userPositionTestObj.companyid = testObj.companyid
    userPositionTestObj.companyname = testObj.companyname
    userPositionTestObj.positionid = testObj.positionid
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
    userTests.companyid = testObj.companyid
    userTests.companyname = testObj.companyname
    userTests.positionid = testObj.positionid
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
def changeTestState(request):
    testId = uuid.UUID(request.GET.get('testId'))
    state = int(request.GET.get('state'))
    testObj = Tests.objects.filter(testid=testId)[0]
    testObj.state = state
    testObj.save()
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
    companyName = request.GET.get('company', None)
    company = CompanyRevLookup.objects.get(companyname=companyName)
    positionsDB = CompanyPosition.objects.filter(companyid=company.companyid)
    positions = OrderedDict()
    positions["DEFAULT"] = "Search for a position"
    for position in positionsDB:
        positions[position.positionid] = position.positionname
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
