from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as loginuser
from django.contrib.auth import logout as logoutuser
from mocktest.algo.test import LinearByTime
from cassandra.cqlengine.query import DoesNotExist
from django.contrib.auth.decorators import user_passes_test
from models import *
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from mocktest.algo.test import TestExceptions
import logging
import DAOUtil
import datetime
import utils
import json
import uuid


logger = logging.getLogger(__name__)
# Create your views here.


def __setAuthInfo(request, context={}):
    context['username'] = ""
    context['isAuthenticated'] = False
    if request.user.is_authenticated():
        context['username'] = request.user.username
        context['isAuthenticated'] = True
    return context


def __brokenPage(request,
                 tile="wrong_way",
                 heading="Something is wrong",
                 info="The information you requested cannot be loaded " +
                      "either because the information is not available " +
                      "or the url is invalid."):
    context = __setAuthInfo(request)
    context["large_tile"] = \
        "/static/mocktest/images/icons/%s_128.png" % tile
    context["small_tile"] = \
        "/static/mocktest/images/icons/%s_64.png" % tile
    context["heading"] = heading
    context["info"] = info
    return render(request, "mocktest/info.html", context)


@login_required(redirect_field_name='redirect_url')
def notVerified(request):
    context = __setAuthInfo(request)
    return render(request, 'mocktest/notVerified.html', context)


def home(request):
    companies = DAOUtil.getDistinctCompanies()
    context = {}
    context['companies'] = companies
    __setAuthInfo(request, context)
    return render(request, 'mocktest/index.html', context)


@login_required(redirect_field_name='redirect_url')
@user_passes_test(lambda u: u.groups.filter(name='UsersVerifiedList').
                  count() == 1,
                  '/notVerified.html')
def advancedTest(request):
    context = {}
    __setAuthInfo(request, context)
    return render(request, 'mocktest/advancedTest.html', context)


@login_required(redirect_field_name='redirect_url')
@user_passes_test(lambda u: u.groups.filter(name='UsersVerifiedList').
                  count() == 1,
                  '/notVerified.html')
def createTest(request):
    username = request.user.username
    # Get the company Name
    companyName = request.GET['companyName']
    # Get the position Name
    positionName = request.GET['positionName']
    # Get optional parameters
    numQ = int(request.GET.get('numQ', 3))
    if numQ > 5:
        numQ = 5
    if numQ < 1:
        numQ = 1
    startTime = request.GET.get('startTime')
    endTime = request.GET.get('endTime')
    testName = request.GET.get('testName')
    if startTime:
        startTime = float(startTime)
    if endTime:
        endTime = float(endTime)
    #   Generating Algorithm (Recent Questions)
    testAlgo = LinearByTime.LinearByTime(username,
                                         companyName,
                                         positionName)
    try:
        testId = testAlgo.createTest(startTime,
                                     endTime,
                                     numQ)
    except TestExceptions.NotEnoughQuestions:
        context = __setAuthInfo(request)
        context["large_tile"] = \
            "/static/mocktest/images/icons/dead_end_128.png"
        context["small_tile"] = "/static/mocktest/images/icons/dead_end_64.png"
        context["heading"] = "Ouch we ran out of questions!"
        context["info"] = "We are either out of questions or an internal " +\
                          "error has occurred. Please give us three to " +\
                          "five days to address this issue. We appreciate " +\
                          "your patience to wait "
        return render(request, "mocktest/info.html", context)
    firstQuestion = testAlgo.getFirstQuestion()
    # Add entry to user scheduled test
    DAOUtil.addScheduledTest(username,
                             testId,
                             testName,
                             companyName,
                             firstQuestion.positionname,
                             firstQuestion.teststarttime,
                             firstQuestion.testendtime,
                             firstQuestion.totalquestions)
    return HttpResponseRedirect("test.html?testId=" + str(testId))


@login_required(redirect_field_name='redirect_url')
@user_passes_test(lambda u: u.groups.filter(name='UsersVerifiedList').
                  count() == 1,
                  '/notVerified.html')
def savedTests(request):
    context = {}
    __setAuthInfo(request, context)
    return render(request, 'mocktest/savedTests.html', context)


@login_required(redirect_field_name='redirect_url')
@user_passes_test(lambda u: u.groups.filter(name='UsersVerifiedList').
                  count() == 1,
                  '/notVerified.html')
def schedTests(request):
    context = {}
    __setAuthInfo(request, context)
    return render(request, 'mocktest/schedTests.html', context)


@login_required(redirect_field_name='redirect_url')
@user_passes_test(lambda u: u.groups.filter(name='UsersVerifiedList').
                  count() == 1,
                  '/notVerified.html')
def viewFavouriteQuestions(request):
    context = __setAuthInfo(request)
    username = request.user.username
    compFavs = UserFavouritesCompanyHash.objects.filter(
                    username=username)
    posFavs = UserFavouritesPositionHash.objects.filter(
                    username=username)
    context['companyNames'] = json.dumps(map(lambda x: x.companyname,
                                             compFavs))
    context['positionNames'] = json.dumps(map(lambda x: x.positionname,
                                              posFavs))
    return render(request, 'mocktest/favourite.html', context)


@login_required(redirect_field_name='redirect_url')
@user_passes_test(lambda u: u.groups.filter(name='UsersVerifiedList').
                  count() == 1,
                  '/notVerified.html')
def viewHistory(request):
    context = {}
    __setAuthInfo(request, context)
    username = request.user.username
    userCompanies = UserCompany.objects.filter(username=username)
    userPositions = UserPosition.objects.filter(username=username)
    context['companyNames'] = json.dumps(map(lambda x: x.companyname,
                                             userCompanies))
    context['positionNames'] = json.dumps(map(lambda x: x.positionname,
                                              userPositions))
    return render(request, 'mocktest/history.html', context)


@login_required(redirect_field_name='redirect_url')
@user_passes_test(lambda u: u.groups.filter(name='UsersVerifiedList').
                  count() == 1,
                  '/notVerified.html')
def test(request):
    if request.method == 'GET':
        # Need to get the testID
        testId = request.GET.get('testId')
        if not testId:
            return __brokenPage(request)
        try:
            questions = Tests.objects.filter(testid=uuid.UUID(testId))
        except ValueError:
            return __brokenPage(request, info="The test-id is broken. " +
                                "Please create another test")
        if len(questions) == 0:
            return __brokenPage(request, info="The test-id is broken. " +
                                "Please create another test")
        if questions[0].username != request.user.username:
            return __brokenPage(request)
        context = {}
        if questions[0].state == Constants.COMPLETED:
            # Test is already completed
            return __brokenPage(request, info="Your test is already completed")
        testStartTime = questions[0].teststarttime
        if testStartTime > datetime.datetime.now():
            # Redirect to countdown page
            return HttpResponseRedirect("countdown.html?testId=" +
                                        testId +
                                        "&testStartTime=" +
                                        str(utils.unix_time(testStartTime)))
        # Set user interaction parameters
        for question in questions:
            try:
                interactions = UserQuestionInteraction.objects.\
                    get(username=request.user.username,
                        questionid=question.questionid).interaction
            except DoesNotExist:
                interactions = []
            question.interactions = {'interactions': interactions}
        context['questions'] = json.dumps(map(
                                lambda x: DAOUtil.jsonReady(
                                    x,
                                    x.interactions),
                                questions))
        return render(request, 'mocktest/test.html', context)


@login_required(redirect_field_name='redirect_url')
@user_passes_test(lambda u: u.groups.filter(name='UsersVerifiedList').
                  count() == 1,
                  '/notVerified.html')
def congrats(request):
    context = {}
    __setAuthInfo(request, context)
    if request.method == 'GET':
        try:
            testId = uuid.UUID(request.GET.get('testId'))
        except ValueError:
            return __brokenPage(request, info="The test-id is broken. " +
                                "Try to find your test under History ")
        except TypeError:
            return __brokenPage(request, info="The test-id is broken. " +
                                "Try to find your test under History ")
        testObj = Tests.objects.get(testid=testId,
                                    questionnum=0)
        if testObj.state != Constants.COMPLETED:
            return __brokenPage(request, info="You haven't completed your " +
                                "test. Try to find your test under Saved " +
                                "Tests.")
        context['testId'] = testId
        return render(request, 'mocktest/congrats.html', context)
    else:
        testId = request.POST["testId"]
        choice = int(request.POST["evaluation"])
        testObj = Tests.objects.get(testid=testId,
                                    questionnum=0)
        logger.debug("testId = " + str(testId) + " choice = " + str(choice))
        if (choice == 1):
            # Enter to the pendingEvaluation Database
            testObj.pendingevaluation = True
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
            testObj.save()
            # Redirect to a success page that tells how
            # the user will be notified when the evaluation is done
        return HttpResponseRedirect("/home.html")


@login_required(redirect_field_name='redirect_url')
@user_passes_test(lambda u: u.groups.filter(name='UsersVerifiedList').
                  count() == 1,
                  '/notVerified.html')
def result(request):
    if request.method == 'GET':
        # Need to get the testID
        try:
            testId = uuid.UUID(request.GET.get('testId'))
        except ValueError:
            return __brokenPage(request, info="The test-id is broken. " +
                                "Try to find your test under History ")
        except TypeError:
            return __brokenPage(request, info="The test-id is broken. " +
                                "Try to find your test under History ")
        isCongrats = request.GET.get('congrats')
        # Check if the test is evaluated
        evaluations = MentorEvaluation.objects.filter(testid=testId)
        questions = Tests.objects.filter(testid=testId)
        if questions[0].username != request.user.username:
            # User not authorized to access the page
            return __brokenPage(request)
        context = {}
        if questions[0].state != 2:
            # Test is Not yet completed
            return __brokenPage(request, info="Your test isn't completed " +
                                "yet. Please finish it before viewing results")
        context['numTabs'] = questions[0].numevaluations
        context['fromCongrats'] = False
        if isCongrats:
            context['fromCongrats'] = True
        context['questions'] = json.dumps(map(lambda x: DAOUtil.jsonReady(x),
                                              questions))
        context['evaluations'] = json.dumps(map(lambda x: DAOUtil.jsonReady(x),
                                                evaluations))
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
        if request.user.is_authenticated():
            return HttpResponse("no")
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
                return HttpResponseRedirect("login.html?invalid=1&" +
                                            "redirect_url=" +
                                            request.POST.get("redirect_url"))
            return HttpResponse("no")

# Should be called by an ajax request


def logout(request):
    logoutuser(request)
    return HttpResponse("ok")


@login_required(redirect_field_name='redirect_url')
@user_passes_test(lambda u: u.groups.filter(name='UsersVerifiedList').
                  count() == 1,
                  '/notVerified.html')
def countDown(request):
    context = {}
    __setAuthInfo(request, context)
    return render(request, 'mocktest/countdown.html', context)


def signup(request):
    if (request.method == 'GET'):
        return render(request, 'mocktest/signup.html', {})
    elif (request.method == 'POST'):
        logger.debug(request.POST.dict())
        DAOUtil.addUser(request.POST["username"],
                        request.POST.get("password"),
                        request.POST.get("fbid"),
                        request.POST.get("firstname"),
                        request.POST.get("lastname"),
                        request.POST.get("email"),
                        request.POST.get("phonenumber"),
                        request.POST.get('ismentor') and True)
        if (request.POST.get("redirect_url")):
            return HttpResponseRedirect(request.POST.get("redirect_url"))
        return HttpResponse("ok")
