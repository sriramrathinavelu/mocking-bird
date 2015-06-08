from Scrapper import *
import logging

logger = logging.getLogger('mocktest.standalone')


class careerCupScrapper(Scrapper):

    def __init__(self, *args, **kwds):
        super(careerCupScrapper, self).__init__(*args, **kwds)
        self.MINANSWERCOUNT = 10
        self.APPLICATIONROOT = 'http://www.careercup.com'
        self.urlPattern = re.compile(self.APPLICATIONROOT +
                                     '/page\?pid=(?P<companyName>.*)' +
                                     '&job=(?P<positionName>.*)' +
                                     '&n=(?P<page>\d+)')
        if not self.urlPattern.match(self.url):
            raise Exception("Invalid URL")

    @staticmethod
    def isSupported(url):
        return "careercup" in url

    def _parseQuestion(self, questionUrl):
        qPage = urllib2.urlopen(questionUrl).read()
        qSoup = BeautifulSoup(qPage)
        questionTextTag = qSoup.find(id="question_preview")\
                               .find(class_="entry").find('a')
        questionText = ""
        for text in questionTextTag.stripped_strings:
            questionText += text + "\n"
        answerTag = qSoup.find_all('div',
                                   id=re.compile('^commentThread\d*$')
                                   )[2].find(class_='commentBody')
        answer = ""
        answerTagChildren = answerTag.children
        for child in answerTagChildren:
            if isinstance(child, Tag) and child.name == 'span':
                break
            if (isinstance(child, NavigableString)):
                answer += str(child)
            else:
                for string in child.stripped_strings:
                    answer += string + "\n"
        return (questionText, answer)

    def _parseQuestionsList(self):
        mainList = self.soup.find(id="question_preview")
        children = mainList.find_all('li')
        for child in children:
            numAnswers = int(child.find(class_="commentCount").string)
            if numAnswers > self.MINANSWERCOUNT:
                link = child.find(class_="entry").find('a')['href']
                yield self.APPLICATIONROOT + link

    def getRawQuestions(self, limit=100):
        count = 0
        while True:
            self._open()
            links = self._parseQuestionsList()
            logger.debug("Scrapping page: " + self.url)
            for link in links:
                try:
                    logger.debug("Scrapping Link: " + link)
                    (question, answer) = self._parseQuestion(link)
                    rawQuestionBank = RawQuestionBank()
                    rawQuestionBank.companyid = self.companyId
                    rawQuestionBank.positionid = self.positionId
                    rawQuestionBank.questionid = TimeUUID.from_datetime(
                                                          datetime.now())
                    rawQuestionBank.questiontype = 3  # Descriptive Answer
                    rawQuestionBank.url = link
                    rawQuestionBank.question = question
                    rawQuestionBank.answer = answer
                    yield rawQuestionBank
                    count += 1
                    if (count >= limit):
                        logger.debug("Retrieved " + str(count) + " questions")
                        return
                except Exception, e:
                    logger.error("Encountered error " + str(e))
            curPage = self.urlPattern.match(self.url).group('page')
            nextPage = str(int(curPage)+1)
            self.url = self.url.replace('&n=' + curPage, '&n=' + nextPage)
