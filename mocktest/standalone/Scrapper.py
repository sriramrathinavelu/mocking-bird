from bs4 import BeautifulSoup, NavigableString, Tag
from cassandra.cqlengine.columns import TimeUUID
from mocktest.models import RawQuestionBank
from datetime import datetime
from mocktest import DAOUtil
import urllib2
import re


class Scrapper(object):

    def __init__(self, *args, **kwds):
        self.url = kwds.get('url')
        self.companyName = kwds.get('companyName')
        self.positionName = kwds.get('positionName')
        if not DAOUtil.isValidCompany(self.companyName):
            raise Exception("Invalid Company")
        if not DAOUtil.isValidPosition(self.positionName):
            raise Exception("Invalid Position")
        self.companyId = DAOUtil.getCompanyId(self.companyName)
        self.positionId = DAOUtil.getPositionId(self.positionName)

    def _open(self):
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent','Mozilla/5.0 (X11; Linux x86_64; rv:2.0.1) Gecko/20110506 Firefox/4.0.1')]
        page = opener.open(self.url).read()
        self.soup = BeautifulSoup(page)

    def getRawQuestions(self):
        pass
