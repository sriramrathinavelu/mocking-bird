import scrapQuestions
scrapQuestions.main()

inst = scrapQuestions.getInstance('http://www.careercup.com/page?pid=amazon-interview-questions&job=software-engineer-developer-interview-questions&n=2','Amazon','Software Developer')

gen = inst.getRawQuestions(50)

for num, rawQuestion in enumerate(gen):
	rawQuestion.save()
	print ("Done " + str(num))
