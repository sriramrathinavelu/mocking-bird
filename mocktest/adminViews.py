from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from cassandra.cqlengine.columns import TimeUUID
from django.http import HttpResponseRedirect
from models import PositionRevLookup
from models import CompanyRevLookup
from models import CompanyPosition
from models import PositionCompany
from models import RawQuestionBank
from models import QuestionBank
from collections import OrderedDict
from django.shortcuts import render
from django.db import connections
from datetime import datetime
from . import adminForms
import collections
import logging
import DAOUtil

logger = logging.getLogger(__name__)


def home(request):
    context = {}
    companyNames = OrderedDict()
    companies = CompanyPosition.objects.all()
    moderateIds = {}
    for company in companies:
        companyNames[company.companyid] = company.companyname
    cursor = connections["cassandra"].cursor()
    results = cursor.execute("""
        SELECT DISTINCT companyid, positionId
        FROM raw_question_bank""")
    for result in results:
        companyName = DAOUtil.getCompanyName(result["companyid"])
        positionName = DAOUtil.getPositionName(result["positionid"])
        moderateIds["companyId=%s&positionId=%s" % (result["companyid"], result["positionid"])] = companyName + "/" + positionName
    context['companyNames'] = companyNames
    context['title'] = 'Home'
    context['moderateIds'] = moderateIds
    return render(request, 'admin/home.html', context)


def addCompany(request):
    context = {}
    context['title'] = 'Add Company'
    context['action'] = 'admin/addCompany.html'
    context['submitValue'] = 'Add'
    if request.method == 'GET':
        form = adminForms.addCompanyForm()
    else:
        form = adminForms.addCompanyForm(request.POST)
        if form.is_valid():
            DAOUtil.addCompanyPosition(form.cleaned_data['companyName'],
                                       form.cleaned_data['positionName'])
            return HttpResponseRedirect('/admin/home.html')
    context['form'] = form
    return render(request, 'admin/genericForm.html', context)


def addPosition(request):
    context = {}
    context['title'] = 'Add Position'
    context['action'] = 'admin/addPosition.html'
    context['submitValue'] = 'Add'
    if request.method == 'GET':
        form = adminForms.addPositionForm()
    else:
        form = adminForms.addPositionForm(request.POST)
        if form.is_valid():
            DAOUtil.addCompanyPosition(form.cleaned_data['companyName'],
                                       form.cleaned_data['positionName'])
            return HttpResponseRedirect('/admin/home.html')
    context['form'] = form
    return render(request, 'admin/genericForm.html', context)


def addQuestion(request):
    context = {}
    context['title'] = 'Add Question'
    context['action'] = '/admin/addQuestion.html'
    context['submitValue'] = 'Add'
    if request.method == 'GET':
        companyId = request.GET["companyId"]
        form = adminForms.addQuestionForm(companyId=companyId)
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
            DAOUtil.addQuestion(form.cleaned_data['companyId'],
                                form.cleaned_data['positionName'],
                                form.cleaned_data['question'],
                                form.cleaned_data['answer'],
                                int(form.cleaned_data['questionType']),
                                choices,
                                form.cleaned_data['input'],
                                form.cleaned_data['key'],
                                timeToSolve)
            return HttpResponseRedirect('/admin/home.html')
    context['form'] = form
    return render(request, 'admin/genericForm.html', context)


def moderateQuestionTable(request):
    companyId = request.GET['companyId']
    positionId = request.GET['positionId']
    rawQuestions = RawQuestionBank.objects.filter(companyid=companyId,
                                                  positionid=positionId)
    paginator = Paginator(rawQuestions, 10)
    page = request.GET.get('page')
    try:
        rawQuestions = paginator.page(page)
    except PageNotAnInteger:
        rawQuestions = paginator.page(1)
    except EmptyPage:
        rawQuestions = paginator.page(paginator.num_pages)

    context = {"rawQuestions": rawQuestions,
               "companyId": companyId,
               "positionId": positionId}
    return render(request, 'admin/moderateQuestionTable.html', context)


def moderateQuestion(request):
    if request.method == 'GET':
        companyId = request.GET['companyId']
        positionId = request.GET['positionId']
        questionId = request.GET['questionId']
        page = request.GET.get('page', 1)
        rawQuestion = RawQuestionBank.objects.filter(companyid=companyId,
                                                     positionid=positionId,
                                                     questionid=questionId)[0]
        rawQuestionForm = adminForms.moderateQuestionForm(rawQuestion=rawQuestion,
                                                          page=page)
        context = {}
        context['form'] = rawQuestionForm
        context['submitValue'] = "Moderate"
        context['action'] = '/admin/moderateQuestion.html'
        context['companyId'] = companyId
        context['positionId'] = positionId
        context['questionId'] = questionId
        context['page'] = page
        return render(request, 'admin/moderateQuestion.html', context)
    else:
        form = adminForms.moderateQuestionForm(request.POST)
        companyId = request.POST['companyId']
        positionId = request.POST['positionId']
        questionId = request.POST['questionId']
        page = request.POST.get('page', 1)
        if form.is_valid():
            rawQuestion = RawQuestionBank.objects.filter(companyid=companyId,
                                                         positionid=positionId,
                                                         questionid=questionId)[0]
            choices = []
            if form.cleaned_data['choices']:
                choices = form.cleaned_data['choices'].split(',')
            timeToSolve = 20
            if form.cleaned_data['timeToSolve']:
                timeToSolve = int(form.cleaned_data['timeToSolve'])
            # DAOUtil.addQuestion(companyId,
            #                     positionId,
            #                     form.cleaned_data['question'],
            #                     form.cleaned_data['answer'],
            #                     form.cleaned_data['questionType'],
            #                     choices,
            #                     form.cleaned_data['input'],
            #                     form.cleaned_data['key'],
            #                     timeToSolve)
            # rawQuestion.delete()
            nextRawQuestion = RawQuestionBank.objects.filter(companyid=companyId,
                                                             positionid=positionId,
                                                             questionid__gt=questionId).limit(1)
            if nextRawQuestion:
                nextRawQuestion = nextRawQuestion[0]
                return HttpResponseRedirect(
                    'admin/moderateQuestion.html?' +
                    'companyId=' + companyId +
                    '&positionId=' + positionId +
                    '&questionId=' + str(nextRawQuestion.questionid) +
                    '&page=' + page)
            else:
                return HttpResponseRedirect(
                    'admin/moderateQuestionTable.html?' +
                    'companyId=' + companyId +
                    '&positionId=' + positionId +
                    '&questionId=' + questionId +
                    '&page=' + page)
    return render(request, 'admin/moderateQuestion.html', context)


def editQuestion(request):
    if request.method == 'GET':
        companyId = request.GET['companyId']
        positionId = request.GET['positionId']
        questionId = request.GET['questionId']
        question = QuestionBank.objects.get(companyid=companyId,
                                            positionid=positionId,
                                            questionid=questionId)
        editQuestionForm = adminForms.editQuestionForm(question=question)
        context = {}
        context['form'] = editQuestionForm
        context['submitValue'] = "Edit"
        context['action'] = '/admin/editQuestion.html'
        context['companyId'] = companyId
        context['positionId'] = positionId
        context['questionId'] = questionId
        return render(request, 'admin/genericForm.html', context)
    else:
        form = adminForms.editQuestionForm(request.POST)
        companyId = request.POST['companyId']
        positionId = request.POST['positionId']
        questionId = request.POST['questionId']
        if form.is_valid():
            question = QuestionBank.objects.get(companyid=companyId,
                                                positionid=positionId,
                                                questionid=questionId)
            choices = []
            if form.cleaned_data['choices']:
                choices = form.cleaned_data['choices'].split(',')
            timeToSolve = 20
            if form.cleaned_data['timeToSolve']:
                timeToSolve = int(form.cleaned_data['timeToSolve'])
            DAOUtil.editQuestion(companyId,
                                 positionId,
                                 questionId,
                                 form.cleaned_data['question'],
                                 form.cleaned_data['answer'],
                                 form.cleaned_data['questionType'],
                                 choices,
                                 form.cleaned_data['input'],
                                 form.cleaned_data['key'],
                                 timeToSolve)
        return HttpResponseRedirect("/admin/home.html")
