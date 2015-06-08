import scrapy
from bs4 import BeautifulSoup, NavigableString, Tag
import re
from codercareer.items import CodercareerItem
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor

def getSourceCode(content):
	code = ""
	for string in content.strings:
		string = string.replace(u'\n', u'')
		string = unicode(string.encode('utf-8').replace('\xc2\xa0', '&nbsp;'))
		string = string.strip().replace('&nbsp;', ' ')
		if not string:
			continue
		code = code + " " + string
	return code

class CoderCareerSpider(CrawlSpider):
	name = "CoderCareer"
	allowed_domains = ['codercareer.blogspot.com']
	start_urls = [
		'http://codercareer.blogspot.com/p/amazon-questions.html'
	]

	rules = (
		#Rule(LinkExtractor(), callback='parsePage', follow=True),
		Rule(LinkExtractor(allow=('/p/')), follow=True),
		Rule(LinkExtractor(allow=('/\d{4}/\d{2}/')), callback='parsePage', follow=True),
		Rule(LinkExtractor(allow=('/search/')), follow=True),
	)

	def parsePage(self, response):
		html = ' '.join(map(lambda x:x.extract(),response.xpath('//*')))
		soup = BeautifulSoup(html)
		entries = soup.find_all('div', class_='post hentry')
		isQuestion = False
		isAnswer = False
		questions = []
		question = ""
		answer = ""
		answers = []
		credits = re.compile('zhedahht@gmail.com|Coding Interviews: Questions|ideone.com')
		sourceCode = re.compile('Consolas')
		for entry in entries:
			item = CodercareerItem() 
			body = entry.find('div', class_='post-body')
			contents = body.find('div').find_all('div')
			# contents are list of div tags containing text.
			# The "\n" in the content is irrelevant and can be removed
			# The span tags inside div can also be discarded
			for content in contents:
				text = ' '.join(content.stripped_strings).replace('\n', ' ').replace('\r', ' ')
				if sourceCode.search(content.get('style', '')):
					text = getSourceCode(content)
				else:
					for child in content.contents:
						if child.name == 'span' and\
							sourceCode.search(child.get('style', '')):
							text = getSourceCode(content)
							break
				if credits.search(text): 
					continue
				#print text
				if text.startswith ('Problem') or text.startswith ('Question'):
					isAnswer = False
					if answer:
						answers.append(answer)
						answer = ""
					isQuestion = True
				if text.startswith ('Analysis'):
					isQuestion = False
					if question:
						questions.append(question)
						question = ""
					isAnswer = True
				if isQuestion:
					question = question + "\n" + text
				if isAnswer:
					answer = answer + "\n" + text
			if isAnswer:
				answers.append(answer)
			item['question'] = '\n'.join(questions)
			item['answer'] = '\n'.join(answers)
			isQuestion = False
			isAnswer = False
			questions = []
			question = ""
			answer = ""
			answers = []
			yield item

