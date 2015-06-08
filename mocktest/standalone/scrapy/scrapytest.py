import urllib2
from bs4 import BeautifulSoup, NavigableString, Tag
import re


def getSourceCode(content):
	#import pdb; pdb.set_trace()
	code = ""
	for string in content.strings:
		string = string.replace(u'\n', u'')
		string = unicode(string.encode('utf-8').replace('\xc2\xa0', '&nbsp;'))
		string = string.strip().replace('&nbsp;', ' ')
		if not string:
			continue
		code = code + " " + string
	return code


url = 'http://codercareer.blogspot.com/'
opener = urllib2.build_opener()
opener.addheaders = [('User-agent','Mozilla/5.0 (X11; Linux x86_64; rv:2.0.1) Gecko/20110506 Firefox/4.0.1')]
html = opener.open(url).read()
#html = ' '.join(map(lambda x:x.extract(),response.xpath('//*')))
soup = BeautifulSoup(html)
entries = soup.find_all('div', class_='post hentry')
isQuestion = False
isAnswer = False
questions = []
question = ""
answer = ""
answers = []
currentEntry = 0
credits = re.compile('zhedahht@gmail.com|Coding Interviews: Questions|ideone.com')
sourceCode = re.compile('Consolas')
for entry in entries:
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


for x,y in zip(questions, answers):
	print "Q:", x
	print "\n\n"
	print "A:", y
	print "\n\n"


