import os
import django 

os.environ["DJANGO_SETTINGS_MODULE"] = "mockingsite.settings"
django.setup()

import scrapQuestions
scrapQuestions.main()

inst = scrapQuestions.getInstance('http://www.careercup.com/page?pid=amazon-interview-questions&job=software-engineer-developer-interview-questions&n=1','Amazon','Software Developer')

gen = inst.getRawQuestions(50)

for num, rawQuestion in enumerate(gen):
	rawQuestion.save()
	print ("Done " + str(num))
