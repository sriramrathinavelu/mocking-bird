from django.contrib.auth.decorators import login_required
from mocktest.models import MentorCompanyPosition
from mocktest.models import MentorPositionCompany
from mocktest.models import MentorCompany
from mocktest.models import MentorPosition
from mocktest.models import CompanyPosition
from mocktest.models import PositionCompany
from mocktest.models import Tests
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.db import connections
from django.shortcuts import render
from collections import defaultdict
from mocktest import DAOUtil
import logging
import json
import cgi


logger = logging.getLogger(__name__)


def __setAuthInfo(request, context={}):
    context['username'] = ""
    context['isAuthenticated'] = False
    if request.user.is_authenticated():
        context['username'] = request.user.username
        context['isAuthenticated'] = True
    return context


@login_required(redirect_field_name='redirect_url')
def home(request):
    context = {}
    __setAuthInfo(request, context)
    return render(request,
                  'mentor/home.html',
                  context)


@login_required(redirect_field_name='redirect_url')
def search(request):
    context = {}
    __setAuthInfo(request, context)
    companies = MentorCompany.objects.filter(
                    username=request.user.username)
    positions = MentorPosition.objects.filter(
                    username=request.user.username)
    context['compList'] = json.dumps(map(lambda x: x.companyname, companies))
    context['posList'] = json.dumps(map(lambda x: x.positionname, positions))
    return render(request,
                  'mentor/search.html',
                  context)


@login_required(redirect_field_name='redirect_url')
def evaluateTest(request):
    if request.method == 'GET':
        # Need to get the testID
        testId = request.GET.get('testId')
        if not testId:
            # Redirect to Invalid test page
            return HttpResponseRedirect("/mentor/home.html")
        questions = Tests.objects.filter(testid=testId)
        context = {}
        if questions[0].state != 2:
            # Test is Not yet completed
            return HttpResponseRedirect("/mentor/home.html")
        context['questions'] = json.dumps(map(lambda x: DAOUtil.jsonReady(x),
                                              questions))
    return render(request, 'mentor/evaluate.html', context)


@login_required(redirect_field_name='redirect_url')
def favourite(request):
    if request.method == 'GET':
        context = {}
        __setAuthInfo(request, context)
        companyPosition = CompanyPosition.objects.all()
        positionCompany = PositionCompany.objects.all()
        mentorCompanyPosition = MentorCompanyPosition.objects.\
            filter(username=request.user.username)
        mentorPositionCompany = MentorPositionCompany.objects.\
            filter(username=request.user.username)
        compPosCheckDict = defaultdict(lambda: {})
        posCompCheckDict = defaultdict(lambda: {})
        compPosDict = defaultdict(lambda: [])
        posCompDict = defaultdict(lambda: [])
        for obj in companyPosition:
            compPosCheckDict[cgi.escape(obj.companyname)][cgi.escape(obj.positionname)] = False
            compPosDict[cgi.escape(obj.companyname)].\
                append(cgi.escape(obj.positionname))
        for obj in mentorCompanyPosition:
            compPosCheckDict[cgi.escape(obj.companyname)][cgi.escape(obj.positionname)] = True
        for obj in positionCompany:
            posCompCheckDict[cgi.escape(obj.positionname)][cgi.escape(obj.companyname)] = False
            posCompDict[cgi.escape(obj.positionname)].\
                append(cgi.escape(obj.companyname))
        for obj in mentorPositionCompany:
            posCompCheckDict[cgi.escape(obj.positionname)][cgi.escape(obj.companyname)] = True
        context['compPosCheckDict'] = json.dumps(compPosCheckDict)
        context['posCompCheckDict'] = json.dumps(posCompCheckDict)
        context['compPosDict'] = json.dumps(compPosDict)
        context['posCompDict'] = json.dumps(posCompDict)
        context['comList'] = json.dumps(compPosDict.keys())
        context['posList'] = json.dumps(posCompDict.keys())
        return render(request,
                      'mentor/favourite.html',
                      context)
    else:
        # POST
        logger.debug(request.POST)
        compPosCheckDict = json.loads(request.POST['compPosCheckDict'])
        posCompCheckDict = json.loads(request.POST['posCompCheckDict'])
        logger.debug(compPosCheckDict)
        logger.debug(posCompCheckDict)
        cursor = connections["cassandra"].cursor()
        cursor.execute("""
            DELETE FROM mentor_company_position
            WHERE username=%s
        """, (request.user.username,))
        cursor.execute("""
            DELETE FROM mentor_position_company
            WHERE username=%s
        """, (request.user.username,))
        cursor.execute("""
            DELETE FROM mentor_company
            WHERE username=%s
        """, (request.user.username,))
        cursor.execute("""
            DELETE FROM mentor_position
            WHERE username=%s
        """, (request.user.username,))
        cursor.close()
        compList = []
        posList = []
        for company, positions in compPosCheckDict.iteritems():
            for position, status in positions.iteritems():
                if (status):
                    mentorCompPos = MentorCompanyPosition()
                    mentorCompPos.username = request.user.username
                    mentorCompPos.companyname = company
                    mentorCompPos.positionname = position
                    mentorCompPos.save()
                    mentorposComp = MentorPositionCompany()
                    mentorposComp.username = request.user.username
                    mentorposComp.positionname = position
                    mentorposComp.companyname = company
                    mentorposComp.save()
                    compList.append(company)
                    posList.append(position)
        for company in set(compList):
            mComp = MentorCompany()
            mComp.username = request.user.username
            mComp.companyname = company
            mComp.save()
        for position in set(posList):
            mPos = MentorPosition()
            mPos.username = request.user.username
            mPos.positionname = position
            mPos.save()
        return HttpResponse("ok")
