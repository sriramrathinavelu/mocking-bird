from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login as loginuser
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as logoutuser
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from models import RawQuestionBank
from models import QuestionBankMedium
from models import MentorRequests
from models import MentorVerifiedRequests
from models import ModeratorVerifiedRequests
from models import CompanyPosition
from models import Moderators
from models import Mentors
from models import Users
from collections import OrderedDict
from django.shortcuts import render
from django.db import connections
from django.conf import settings
from . import adminForms
import logging
import DAOUtil
import auditor
import urllib2
import mailer
import os

logger = logging.getLogger(__name__)


def saveQuestionImageFile(fileName, fileData):
    with open(os.path.join(
                settings.MEDIA_ROOT,
                'images',
                'questions',
                fileName), 'wb+') as openedFile:
        for chunk in fileData.chunks():
            openedFile.write(chunk)


def adminChecks(func):
    def newFunc(*args, **kwds):
        request = args[0]
        if not request.user.is_staff:
            return HttpResponse("You are not authorized to view this page")
        return func(*args, **kwds)
    return newFunc


def __metaView(request, context={}):
    context['isLoggedIn'] = False
    context['isStaff'] = False
    context['isValidated'] = False
    context['isSuperUser'] = False
    context['username'] = ""
    if not request.user.is_authenticated():
        context['isLoggedIn'] = False
    else:
        context['isLoggedIn'] = True
        context['username'] = request.user.username
        if request.user.groups.filter(
            name='ModeratorsVerifiedList'
        ).count() == 1:
            context['isValidated'] = True
        if request.user.is_staff:
            context['isStaff'] = True
        if request.user.is_superuser:
            context['isSuperUser'] = True
    return context


@login_required
def logout(request):
    logoutuser(request)
    if (request.POST.get("redirect_url")):
        return HttpResponseRedirect(request.POST.get("redirect_url"))
    else:
        return HttpResponseRedirect("/admin/home.html")


def login(request):
    if request.method == 'GET':
        context = {}
        context['title'] = 'Moderator Login'
        context['action'] = '/admin/moderatorLogin.html'
        context['submitValue'] = 'Login'
        if request.user.is_authenticated():
            logger.debug("User already authenticated.Redirect url is",
                         request.GET.get("redirect_url"))
            if request.GET.get("redirect_url"):
                return render(request, request.GET.get("redirect_url"), {})
            else:
                return HttpResponseRedirect("/admin/home.html")
        form = adminForms.loginForm()
        context['form'] = form
        context['message'] = ""
        if request.GET.get("invalid"):
            context['message'] = "The supplied credentials are invalid" + \
                ". Please try again"
        return render(request, 'admin/genericForm-no-login.html', context)
    else:
        form = adminForms.loginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                user = authenticate(username=username,
                                    password=password,
                                    fbid=None,
                                    isInternal=False)
                if user:
                    loginuser(request, user)
                    if (request.POST.get("redirect_url")):
                        return HttpResponseRedirect(
                            request.POST.get("redirect_url")
                        )
                    return HttpResponseRedirect("/admin/home.html")
                else:
                    context['message'] = "The supplied credentials" + \
                        " are invalid. Please try again"
            except Exception, e:
                context['message'] = "Encountered error: " + str(e)
        return render(request, 'admin/genericForm-no-login.html', context)


def home(request):
    context = __metaView(request)
    companyNames = OrderedDict()
    cursor = connections["cassandra"].cursor()
    companies = cursor.execute("""
        SELECT DISTINCT companyname
        FROM company_position
        """)
    for company in companies:
        companyNames[urllib2.quote(company["companyname"])] = \
            company["companyname"]
    moderateIds = {}
    results = cursor.execute("""
        SELECT DISTINCT companyname, positionname
        FROM raw_question_bank""")
    for result in results:
        companyName = result["companyname"]
        positionName = result["positionname"]
        moderateIds[
            "companyName=%s&positionName=%s" % (
                urllib2.quote(companyName),
                urllib2.quote(positionName))
        ] = companyName + "/" + positionName
    companyPositions = cursor.execute("""
        SELECT companyname, positionname
        FROM company_position
    """)
    companyPositionsDict = OrderedDict()
    for companyPosition in companyPositions:
        companyName = companyPosition["companyname"]
        positionName = companyPosition["positionname"]
        companyPositionsDict[
            "companyName=%s&positionName=%s" % (
                urllib2.quote(companyName),
                urllib2.quote(positionName))
        ] = companyName + "/" + positionName
    context['companyNames'] = companyNames
    context['title'] = 'Home'
    context['moderateIds'] = moderateIds
    context['companyPositionsDict'] = companyPositionsDict
    cursor.close()
    return render(request, 'admin/home.html', context)


def signup(request):
    context = {}
    context['title'] = 'Moderator Sign-up'
    context['action'] = '/admin/moderatorSignUp.html'
    context['submitValue'] = 'SignUp'
    message = ""
    if request.method == 'GET':
        form = adminForms.signUpForm()
    else:
        form = adminForms.signUpForm(request.POST)
        if form.is_valid():
            try:
                done = DAOUtil.addUser(form.cleaned_data['username'],
                                       form.cleaned_data['password'],
                                       None,
                                       form.cleaned_data['firstName'],
                                       form.cleaned_data['lastName'],
                                       form.cleaned_data['email'],
                                       form.cleaned_data['phone'],
                                       form.cleaned_data['ianatimezone'],
                                       isMentor=False,
                                       isInternal=True)
            except Exception, e:
                done = False
                message = str(e)
            if done:
                return HttpResponseRedirect('/admin/home.html')
    context['form'] = form
    context['message'] = message
    return render(request, 'admin/genericForm-no-login.html', context)


def error(request):
    context = {}
    context['title'] = 'oops'
    return render(request, 'admin/error.html', context)


@login_required(redirect_field_name="redirect_url",
                login_url='admin/moderatorLogin.html')
def addCompany(request):
    context = __metaView(request)
    context['title'] = 'Add Company'
    context['action'] = '/admin/addCompany.html'
    context['submitValue'] = 'Add'
    if request.method == 'GET':
        form = adminForms.addCompanyForm()
    else:
        form = adminForms.addCompanyForm(request.POST)
        if form.is_valid():
            done = DAOUtil.\
                addCompanyPosition(form.cleaned_data['companyName'],
                                   form.cleaned_data['positionName'],
                                   form.cleaned_data['minQuestions'],
                                   form.cleaned_data['minDuration'],
                                   form.cleaned_data['minQPerPool'],
                                   form.cleaned_data['maxPools'],
                                   form.cleaned_data['poolIncrementCount'])
            if done:
                auditor.audit(
                    username=request.user.username,
                    action=auditor.AuditingActions.ADDCOMPANY,
                    args={
                        'Company Name': form.cleaned_data['companyName'],
                        'Position Name': form.cleaned_data['positionName'],
                        'Min Questions': form.cleaned_data['minQuestions'],
                        'Min Duration': form.cleaned_data['minDuration'],
                    }
                )
                return HttpResponseRedirect('/admin/home.html')
            else:
                return HttpResponseRedirect('/admin/error.html')
    context['form'] = form
    return render(request, 'admin/genericForm.html', context)


@login_required(redirect_field_name="redirect_url",
                login_url='admin/moderatorLogin.html')
def addPosition(request):
    context = __metaView(request)
    context['title'] = 'Add Position'
    context['action'] = '/admin/addPosition.html'
    context['submitValue'] = 'Add'
    if request.method == 'GET':
        form = adminForms.addPositionForm()
    else:
        form = adminForms.addPositionForm(request.POST)
        if form.is_valid():
            done = DAOUtil.\
                addCompanyPosition(form.cleaned_data['companyName'],
                                   form.cleaned_data['positionName'],
                                   form.cleaned_data['minQuestions'],
                                   form.cleaned_data['minDuration'],
                                   form.cleaned_data['minQPerPool'],
                                   form.cleaned_data['maxPools'],
                                   form.cleaned_data['poolIncrementCount'])
            if done:
                auditor.audit(
                    username=request.user.username,
                    action=auditor.AuditingActions.ADDPOSITION,
                    args={
                        'Company Name': form.cleaned_data['companyName'],
                        'Position Name': form.cleaned_data['positionName'],
                        'Min Questions': form.cleaned_data['minQuestions'],
                        'Min Duration': form.cleaned_data['minDuration'],
                    }
                )
                return HttpResponseRedirect('/admin/home.html')
            else:
                return HttpResponseRedirect('/admin/error.html')
    context['form'] = form
    return render(request, 'admin/genericForm.html', context)


@login_required(redirect_field_name="redirect_url",
                login_url='admin/moderatorLogin.html')
def editPosition(request):
    context = __metaView(request)
    context['title'] = 'Edit Position'
    context['action'] = '/admin/editPosition.html'
    context['submitValue'] = 'Edit'
    if request.method == 'GET':
        companyName = request.GET["companyName"]
        positionName = request.GET["positionName"]
        companyPositionObj = CompanyPosition.objects.get(
            companyname=companyName,
            positionname=positionName
        )
        form = adminForms.editPositionForm(
            companyPositionObj=companyPositionObj
        )
    else:
        form = adminForms.editPositionForm(request.POST)
        if form.is_valid():
            done = DAOUtil.\
                editCompanyPosition(form.cleaned_data['companyName'],
                                    form.cleaned_data['positionName'],
                                    form.cleaned_data['minQuestions'],
                                    form.cleaned_data['minDuration'],
                                    form.cleaned_data['minQPerPool'],
                                    form.cleaned_data['maxPools'],
                                    form.cleaned_data['poolIncrementCount'],
                                    form.cleaned_data['poolCount'],
                                    form.cleaned_data['currentPool'])
            if done:
                auditor.audit(
                    username=request.user.username,
                    action=auditor.AuditingActions.EDITPOSITION,
                    args={
                        'Company Name': form.cleaned_data['companyName'],
                        'Position Name': form.cleaned_data['positionName'],
                        'Min Questions': form.cleaned_data['minQuestions'],
                        'Min Duration': form.cleaned_data['minDuration'],
                    }
                )
                return HttpResponseRedirect('/admin/home.html')
            else:
                return HttpResponseRedirect('/admin/error.html')
    context['form'] = form
    return render(request, 'admin/genericForm.html', context)


@login_required(redirect_field_name="redirect_url",
                login_url='admin/moderatorLogin.html')
def addQuestion(request):
    context = __metaView(request)
    context['title'] = 'Add Question'
    context['action'] = '/admin/addQuestion.html'
    context['submitValue'] = 'Add'
    if request.method == 'GET':
        companyName = request.GET["companyName"]
        form = adminForms.addQuestionForm(companyName=companyName)
    else:
        form = adminForms.addQuestionForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['choices']:
                choices = ','.split(form.cleaned_data['choices'])
            else:
                choices = []
            if form.cleaned_data['timeToSolve']:
                timeToSolve = int(form.cleaned_data['timeToSolve'])
            else:
                timeToSolve = None
            questionObj = DAOUtil.\
                addQuestion(form.cleaned_data['companyName'],
                            form.cleaned_data['positionName'],
                            form.cleaned_data['question'],
                            form.cleaned_data['answer'],
                            int(form.cleaned_data['questionType']),
                            choices,
                            form.cleaned_data['input'],
                            form.cleaned_data['key'],
                            timeToSolve)
            auditor.audit(
                username=request.user.username,
                action=auditor.AuditingActions.ADDQUESTION,
                args={
                    'Company Name': form.cleaned_data['companyName'],
                    'Position Name': form.cleaned_data['positionName'],
                    'Class Label': questionObj.classlabel,
                    'Pool': str(questionObj.pool),
                    'Question Id': str(questionObj.questionid),
                }
            )
            if request.FILES.get('imageFile'):
                saveQuestionImageFile(
                    str(questionObj.questionid),
                    request.FILES.get('imageFile')
                )
            return HttpResponseRedirect('/admin/home.html')
    context['form'] = form
    return render(request, 'admin/genericForm.html', context)


def verification(request):
    username = request.GET['username']
    # Add some hash check here

    user = Users.objects.get(username=username)
    authUser = User.objects.get(username=username)
    if authUser.groups.filter(name='UsersWaitingList').count() != 0:
        try:
            UserVerGrp = Group.objects.get(
                            name='UsersVerifiedList'
                          )
        except Group.DoesNotExist:
            UserVerGrp = Group(name='UsersVerifiedList')
            UserVerGrp.save()
        authUser.groups.remove(
            authUser.groups.get(name='UsersWaitingList')
        )
        authUser.groups.add(UserVerGrp)
        authUser.save()
    if user.isinternal:
        if authUser.groups.filter(name='ModeratorsWaitingList').count() != 0:
            moderatorVerReq = ModeratorVerifiedRequests()
            moderatorVerReq.username = user.username
            moderatorVerReq.firstname = user.firstname
            moderatorVerReq.lastname = user.lastname
            moderatorVerReq.email = user.email
            moderatorVerReq.phone = user.phone
            moderatorVerReq.save()
            try:
                moderatorVerGrp = Group.objects.get(
                                    name='ModeratorsVerifiedList'
                                  )
            except Group.DoesNotExist:
                moderatorVerGrp = Group(name='ModeratorsVerifiedList')
                moderatorVerGrp.save()
            authUser.groups.remove(
                authUser.groups.get(name='ModeratorsWaitingList')
            )
            authUser.groups.add(moderatorVerGrp)
            authUser.save()
    if user.mentorrequest:
        # Check if user is in mentor waiting list
        if authUser.groups.filter(name='MentorsWaitingList').count() != 0:
            mentorReq = MentorRequests.objects.get(username=username)
            mentorVerReq = MentorVerifiedRequests()
            mentorVerReq.username = mentorReq.username
            mentorVerReq.firstname = mentorReq.firstname
            mentorVerReq.lastname = mentorReq.lastname
            mentorVerReq.email = mentorReq.email
            mentorVerReq.phone = mentorReq.phone
            mentorVerReq.companyname = mentorReq.companyname
            mentorVerReq.positionname = mentorReq.positionname
            mentorVerReq.save()
            mentorReq.delete()
            try:
                mentorVerGrp = Group.objects.get(name='MentorsVerifiedList')
            except Group.DoesNotExist:
                mentorVerGrp = Group(name='MentorsVerifiedList')
                mentorVerGrp.save()
            authUser.groups.remove(
                authUser.groups.get(name='MentorsWaitingList')
            )
            authUser.groups.add(mentorVerGrp)
            authUser.save()
    # Redirect to some pretty thank you page

    context = {}
    context['username'] = username
    context['isAuthenticated'] = False
    return render(request, 'mocktest/verification.html', context)
    # return HttpResponse("Thanks for verifying!")


@login_required(redirect_field_name="redirect_url",
                login_url='admin/moderatorLogin.html')
def moderateMentorsTable(request):
    context = __metaView(request)
    mentorReqs = MentorVerifiedRequests.objects.all()
    paginator = Paginator(mentorReqs, 10)
    page = request.GET.get('page')
    try:
        mentorReqs = paginator.page(page)
    except PageNotAnInteger:
        mentorReqs = paginator.page(1)
    except EmptyPage:
        mentorReqs = paginator.page(paginator.num_pages)
    context["mentorReqs"] = mentorReqs
    return render(request, 'admin/moderateMentorsTable.html', context)


@login_required(redirect_field_name="redirect_url",
                login_url='admin/moderatorLogin.html')
def moderateMentor(request):
    context = __metaView(request)
    username = request.GET['username']
    mentorReq = MentorVerifiedRequests.objects.filter(username=username)
    context["mentorReq"] = mentorReq
    return render(request, 'admin/moderateMentor.html', context)


@login_required(redirect_field_name="redirect_url",
                login_url='admin/moderatorLogin.html')
def acceptMentor(request):
    username = request.GET['username']
    mentorVerReq = MentorVerifiedRequests.objects.get(username=username)
    mentor = Mentors()
    mentor.username = mentorVerReq.username
    mentor.firstname = mentorVerReq.firstname
    mentor.lastname = mentorVerReq.lastname
    mentor.email = mentorVerReq.email
    mentor.phone = mentorVerReq.phone
    mentor.companyname = mentorVerReq.companyname
    mentor.positionname = mentorVerReq.positionname
    mentor.save()
    mentorVerReq.delete()
    try:
        mentorGrp = Group.objects.get(name='Mentors')
    except Group.DoesNotExist:
        mentorGrp = Group(name='Mentors')
        mentorGrp.save()
    authUser = User.objects.get(username=username)
    authUser.groups.remove(
        authUser.groups.get(name='MentorsVerifiedList')
    )
    authUser.groups.add(mentorGrp)
    authUser.save()
    # Auditing the action
    auditor.audit(
        username=request.user.username,
        action=auditor.AuditingActions.MODERATEMENTOR,
        args={
            'User Name': mentorVerReq.username,
            'First Name': mentorVerReq.firstname,
            'Last Name': mentorVerReq.lastname,
        }
    )
    # Trigger an E-mail response to the mentor
    mailer.sendMail(
        emailAddr=mentorVerReq.email,
        code=mailer.PostOffice.MENTOR_APPROVED,
        _dict={
            'username': mentorVerReq.username,
            'mentorURL': 'http://crackit.com:8000/mentor/home.html',
        }
    )
    return HttpResponseRedirect('/admin/moderateMentorsTable.html')


@login_required(redirect_field_name="redirect_url",
                login_url='admin/moderatorLogin.html')
def moderateQuestionTable(request):
    companyName = request.GET['companyName']
    positionName = request.GET['positionName']
    rawQuestions = RawQuestionBank.objects.filter(companyname=companyName,
                                                  positionname=positionName)
    paginator = Paginator(rawQuestions, 10)
    page = request.GET.get('page')
    try:
        rawQuestions = paginator.page(page)
    except PageNotAnInteger:
        rawQuestions = paginator.page(1)
    except EmptyPage:
        rawQuestions = paginator.page(paginator.num_pages)

    context = {"rawQuestions": rawQuestions,
               "companyName": companyName,
               "positionName": positionName}
    context = __metaView(request, context)
    return render(request, 'admin/moderateQuestionTable.html', context)


@login_required(redirect_field_name="redirect_url",
                login_url='admin/moderatorLogin.html')
def addModeratorsTable(request):
    context = __metaView(request)
    moderatorReqs = ModeratorVerifiedRequests.objects.all()
    paginator = Paginator(moderatorReqs, 10)
    page = request.GET.get('page')
    try:
        moderatorReqs = paginator.page(page)
    except PageNotAnInteger:
        moderatorReqs = paginator.page(1)
    except EmptyPage:
        moderatorReqs = paginator.page(paginator.num_pages)
    context["moderatorReqs"] = moderatorReqs
    return render(request, 'admin/addModeratorsTable.html', context)


@login_required(redirect_field_name="redirect_url",
                login_url='admin/moderatorLogin.html')
def addModerator(request):
    username = request.GET['username']
    moderatorVerReq = ModeratorVerifiedRequests.objects.get(username=username)
    moderator = Moderators()
    moderator.username = moderatorVerReq.username
    moderator.firstname = moderatorVerReq.firstname
    moderator.lastname = moderatorVerReq.lastname
    moderator.email = moderatorVerReq.email
    moderator.phone = moderatorVerReq.phone
    moderator.save()
    moderatorVerReq.delete()
    try:
        moderatorGrp = Group.objects.get(name='Moderators')
    except Group.DoesNotExist:
        moderatorGrp = Group(name='Moderators')
        moderatorGrp.save()
    authUser = User.objects.get(username=username)
    authUser.groups.remove(
        authUser.groups.get(name='ModeratorsVerifiedList'))
    authUser.groups.add(moderatorGrp)
    authUser.is_staff = True
    authUser.save()
    # Auditing the action
    auditor.audit(
        username=request.user.username,
        action=auditor.AuditingActions.MODERATEMENTOR,
        args={
            'User Name': moderatorVerReq.username,
            'First Name': moderatorVerReq.firstname,
            'Last Name': moderatorVerReq.lastname,
        }
    )
    # Trigger an E-mail response to the mentor
    mailer.sendMail(
        emailAddr=moderatorVerReq.email,
        code=mailer.PostOffice.MODERATOR_APPROVED,
        _dict={
            'username': moderatorVerReq.username,
            'mentorURL': 'http://crackit.com:8000/admin/home.html',
        }
    )
    return HttpResponseRedirect('/admin/moderateMentorsTable.html')


@login_required(redirect_field_name="redirect_url",
                login_url='admin/moderatorLogin.html')
def moderateQuestion(request):
    if request.method == 'GET':
        companyName = request.GET['companyName']
        positionName = request.GET['positionName']
        questionId = request.GET['questionId']
        page = request.GET.get('page', 1)
        rawQuestion = RawQuestionBank.objects.filter(companyname=companyName,
                                                     positionname=positionName,
                                                     questionid=questionId)[0]
        rawQuestionForm = adminForms.\
            moderateQuestionForm(rawQuestion=rawQuestion,
                                 page=page)
        context = {}
        context['form'] = rawQuestionForm
        context['submitValue'] = "Moderate"
        context['action'] = '/admin/moderateQuestion.html'
        context['companyName'] = companyName
        context['positionName'] = positionName
        context['questionId'] = questionId
        context['page'] = page
        context = __metaView(request, context)
        return render(request, 'admin/moderateQuestion.html', context)
    else:
        form = adminForms.moderateQuestionForm(request.POST)
        companyName = request.POST['companyName']
        positionName = request.POST['positionName']
        questionId = request.POST['questionId']
        page = request.POST.get('page', 1)
        if form.is_valid():
            rawQuestion = RawQuestionBank.objects.\
                filter(companyname=companyName,
                       positionname=positionName,
                       questionid=questionId)[0]
            choices = []
            if form.cleaned_data['choices']:
                choices = form.cleaned_data['choices'].split(',')
            timeToSolve = 20
            if form.cleaned_data['timeToSolve']:
                timeToSolve = int(form.cleaned_data['timeToSolve'])
            DAOUtil.addQuestion(companyName,
                                positionName,
                                form.cleaned_data['question'],
                                form.cleaned_data['answer'],
                                form.cleaned_data['questionType'],
                                choices,
                                form.cleaned_data['input'],
                                form.cleaned_data['key'],
                                timeToSolve)
            rawQuestion.delete()
            nextRawQuestion = RawQuestionBank.objects.\
                filter(companyname=companyName,
                       positionname=positionName,
                       questionid__gt=questionId).limit(1)
            if nextRawQuestion:
                nextRawQuestion = nextRawQuestion[0]
                return HttpResponseRedirect(
                    'admin/moderateQuestion.html?' +
                    'companyName=' + companyName +
                    '&positionName=' + positionName +
                    '&questionId=' + str(nextRawQuestion.questionid) +
                    '&page=' + page)
            else:
                return HttpResponseRedirect(
                    'admin/moderateQuestionTable.html?' +
                    'companyName=' + companyName +
                    '&positionName=' + positionName +
                    '&questionId=' + questionId +
                    '&page=' + page)
    return render(request, 'admin/moderateQuestion.html', context)


@login_required(redirect_field_name="redirect_url",
                login_url='admin/moderatorLogin.html')
def editQuestion(request):
    if request.method == 'GET':
        companyName = request.GET['companyName']
        positionName = request.GET['positionName']
        questionId = request.GET['questionId']
        question = QuestionBankMedium.objects.get(companyname=companyName,
                                                  positionname=positionName,
                                                  questionid=questionId)
        editQuestionForm = adminForms.editQuestionForm(question=question)
        context = {}
        context['form'] = editQuestionForm
        context['submitValue'] = "Edit"
        context['action'] = '/admin/editQuestion.html'
        context['companyName'] = companyName
        context['positionName'] = positionName
        context['questionId'] = questionId
        context = __metaView(request, context)
        return render(request, 'admin/genericForm.html', context)
    else:
        form = adminForms.editQuestionForm(request.POST)
        companyName = request.POST['companyName']
        positionName = request.POST['positionName']
        questionId = request.POST['questionId']
        if form.is_valid():
            question = QuestionBankMedium.objects.get(
                companyname=companyName,
                positionname=positionName,
                questionid=questionId
            )
            choices = []
            if form.cleaned_data['choices']:
                choices = form.cleaned_data['choices'].split(',')
            timeToSolve = 20
            if form.cleaned_data['timeToSolve']:
                timeToSolve = int(form.cleaned_data['timeToSolve'])
            questionObj = DAOUtil.\
                editQuestion(companyName,
                             positionName,
                             questionId,
                             form.cleaned_data['question'],
                             form.cleaned_data['answer'],
                             form.cleaned_data['questionType'],
                             choices,
                             form.cleaned_data['input'],
                             form.cleaned_data['key'],
                             timeToSolve)
            auditor.audit(
                username=request.user.username,
                action=auditor.AuditingActions.EDITQUESTION,
                args={
                    'Company Name': form.cleaned_data['companyName'],
                    'Position Name': form.cleaned_data['positionName'],
                    'Class Label': questionObj.classlabel,
                    'Pool': questionObj.pool,
                    'Question Id': str(questionObj.questionid),
                }
            )
        return HttpResponseRedirect("/admin/home.html")
