from django.contrib.auth import authenticate, login as loginuser
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from mocktest.models import MentorCompanyPosition
from mocktest.models import CompanyPosition
from mocktest.models import PositionCompany
from django.shortcuts import render
from collections import defaultdict
from mocktest import DAOUtil
import logging
import json


logger = logging.getLogger(__name__)


def __setAuthInfo(request, context={}):
    context['username'] = ""
    context['isAuthenticated'] = False
    if request.user.is_authenticated():
        context['username'] = request.user.username
        context['isAuthenticated'] = True
    return context


def home(request):
    context = {}
    __setAuthInfo(request, context)
    return render(request,
                  'mentor/home.html',
                  context)


def favourite(request):
    context = {}
    __setAuthInfo(request, context)
    companyPosition = CompanyPosition.objects.all()
    positionCompany = PositionCompany.objects.all()
    mentorCompanyPosition = MentorCompanyPosition.objects.\
        filter(username=request.user.username)
    mentorCompPosDict = {}
    for obj in mentorCompanyPosition:

    compPosDict = {}
    posCompDict = {}
    for obj in companyPosition:


    context['compPosDict'] = compPosDict
    context['posCompDict'] = posCompDict
    return render(request,
                  'mentor/favourite.html',
                  context)
