from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as loginuser
from django.contrib.auth import logout as logoutuser
from mocktest.algo.test import LinearByTime
from models import CompanyRevLookup
from models import UserCompany
from models import UserPosition
from django.shortcuts import render
from models import Users, Tests
from django.http import HttpResponseRedirect
from django.http import HttpResponse
import logging
import DAOUtil
import datetime
import utils
import json


logger = logging.getLogger(__name__)
# Create your views here.


def home(request):
    companies = CompanyRevLookup.objects.all()
    context = {}
    context['companies'] = json.dumps(map(lambda x: x.companyname,
                                      companies))
    context['username'] = ""
    context['isAuthenticated'] = False
    if request.user.is_authenticated():
        context['username'] = request.user.username
        context['isAuthenticated'] = True
    return render(request, 'mocktest/index.html', context)


@login_required(redirect_field_name='redirect_url')
def advancedTest(request):
    return render(request, 'mocktest/advancedTest.html', {})


@login_required(redirect_field_name='redirect_url')
def createTest(request):
    username = request.user.username
    # Get the company ID
    companyName = request.GET['companyName']
    companyId = DAOUtil.getCompanyId(companyName=companyName)
    # Get the position ID
    positionId = request.GET['positionId']
    # Get optional parameters
    numQ = int(request.GET.get('numQ', 3))
    if numQ > 5:
        numQ = 5
    if numQ < 1:
        numQ = 1
    startTime = request.GET.get('startTime')
    endTime = request.GET.get('endTime')
    testName = request.GET.get('testName')
    logger.debug("Start Time: " + startTime + " End Time: " + endTime)
    if startTime:
        startTime = float(startTime)
    if endTime:
        endTime = float(endTime)
    #   Generating Algorithm (Recent Questions)
    testAlgo = LinearByTime.LinearByTime(username, companyId, positionId)
    testId = testAlgo.createTest(startTime,
                                 endTime,
                                 numQ)
    firstQuestion = testAlgo.getFirstQuestion()
    # Add entry to user scheduled test
    DAOUtil.addScheduledTest(username,
                             testId,
                             testName,
                             companyId,
                             companyName,
                             positionId,
                             firstQuestion.positionname,
                             firstQuestion.teststarttime,
                             firstQuestion.testendtime,
                             firstQuestion.totalquestions)
    return HttpResponseRedirect("test.html?testId=" + str(testId))


@login_required(redirect_field_name='redirect_url')
def savedTests(request):
    return render(request, 'mocktest/savedTests.html', {})


@login_required(redirect_field_name='redirect_url')
def schedTests(request):
    return render(request, 'mocktest/schedTests.html', {})


@login_required(redirect_field_name='redirect_url')
def viewHistory(request):
    username = request.user.username
    userCompanies = UserCompany.objects.filter(username=username)
    userPositions = UserPosition.objects.filter(username=username)
    context = {}
    context['companyNames'] = json.dumps(map(lambda x: x.companyname,
                                             userCompanies))
    context['companyMap'] = json.dumps(dict(
                                        map(lambda x:
                                            DAOUtil.jsonReady((x.companyname,
                                                               x.companyid)),
                                            userCompanies)))
    context['positionNames'] = json.dumps(map(lambda x: x.positionname,
                                              userPositions))
    context['positionMap'] = json.dumps(dict(
                                        map(lambda x:
                                            DAOUtil.jsonReady((x.positionname,
                                                               x.positionid)),
                                            userPositions)))
    return render(request, 'mocktest/history.html', context)


@login_required(redirect_field_name='redirect_url')
def test(request):
    if request.method == 'GET':
        # Need to get the testID
        testId = request.GET.get('testId')
        if not testId:
            # Redirect to Invalid test page
            return HttpResponseRedirect("home.html")
        questions = Tests.objects.filter(testid=testId)
        if questions[0].username != request.user.username:
            # User not authorized to access the page
            return HttpResponseRedirect("home.html")
        context = {}
        if questions[0].state == 2:
            # Test is already completed
            return HttpResponseRedirect("home.html")
        testStartTime = questions[0].teststarttime
        if testStartTime > datetime.datetime.now():
            # Redirect to countdown page
            return HttpResponseRedirect("countdown.html?testId=" +
                                        testId +
                                        "&testStartTime=" +
                                        str(utils.unix_time(testStartTime)))
        context['questions'] = json.dumps(map(lambda x: DAOUtil.jsonReady(x),
                                              questions))
        return render(request, 'mocktest/test.html', context)


@login_required(redirect_field_name='redirect_url')
def congrats(request):
    if request.method == 'GET':
        context = {}
        testId = request.GET.get('testId')
        if not testId:
            # 404 page
            # Also check if this test is completed
            return HttpResponseRedirect("/home.html")
        context['testId'] = testId
        context['isAuthenticated'] = False
        if request.user.is_authenticated():
            context['username'] = request.user.username
            context['isAuthenticated'] = True
        return render(request, 'mocktest/congrats.html', context)
    else:
        testId = request.POST["testId"]
        choice = request.POST["evaluation"]
        logger.debug("testId = " + testId + " choice = " + choice)


@login_required(redirect_field_name='redirect_url')
def result(request):
    if request.method == 'GET':
        # Need to get the testID
        testId = request.GET.get('testId')
        if not testId:
            # Redirect to Invalid test page
            return HttpResponseRedirect("home.html")
        questions = Tests.objects.filter(testid=testId)
        if questions[0].username != request.user.username:
            # User not authorized to access the page
            return HttpResponseRedirect("home.html")
        context = {}
        if questions[0].state != 2:
            # Test is Not yet completed
            return HttpResponseRedirect("home.html")
        context['questions'] = json.dumps(map(lambda x: DAOUtil.jsonReady(x),
                                              questions))
        return render(request, 'mocktest/result.html', context)


def login(request):
    if (request.method == 'GET'):
        if request.user.is_authenticated():
            logger.debug("User already authenticated.Redirect url is",
                         request.GET.get("redirect_url"))
            if request.GET.get("redirect_url"):
                return render(request, request.GET.get("redirect_url"), {})
            else:
                return HttpResponseRedirect("home.html")
        return render(request, 'mocktest/login.html', {})
    else:
        # POST

        username = request.POST["username"]
        password = request.POST.get("password", request.POST.get("fbid"))
        fbid = request.POST.get("fbid")
        user = authenticate(username=username, password=password, fbid=fbid)
        if (user):
            loginuser(request, user)
            if (request.POST.get("redirect_url")):
                return HttpResponseRedirect(request.POST.get("redirect_url"))
            return HttpResponse("ok")
        else:
            if (request.POST.get("redirect_url")):
                return HttpResponseRedirect("login.html/invalid=1&" +
                                            "redirect_url=" +
                                            request.POST.get("redirect_url"))
            return HttpResponse("no")

# Should be called by an ajax request


def logout(request):
    logoutuser(request)
    return HttpResponse("ok")


@login_required(redirect_field_name='redirect_url')
def countDown(request):
    return render(request, 'mocktest/countdown.html', {})


def signup(request):
    if (request.method == 'GET'):
        return render(request, 'mocktest/signup.html', {})
    elif (request.method == 'POST'):
        logger.debug(request.POST.dict())
        newUser = Users()
        newUser.username = request.POST["username"]
        password = request.POST.get("password", request.POST.get("fbid", None))
        newUser.password = password
        newUser.firstname = request.POST["firstname"]
        newUser.lastname = request.POST["lastname"]
        newUser.email = request.POST["email"]
        phonenumber = request.POST.get("phonenumber", None)
        if (phonenumber and phonenumber.startswith("Phone")):
            phonenumber = None
        newUser.phone = phonenumber
        newUser.fbid = request.POST.get("fbid", None)
        newUser.rating = 1200
        curtime = datetime.datetime.now()
        newUser.ctime = curtime
        newUser.mtime = curtime
        newUser.save()
        authUser = User(username=request.POST["username"],
                        password='mockingsite')
        authUser.is_staff = True
        # Hack to make it work in openshift
        authUser.last_login = datetime.datetime.now()
        authUser.save()
        if (request.POST.get("redirect_url")):
            return HttpResponseRedirect(request.POST.get("redirect_url"))
        return HttpResponse("ok")
