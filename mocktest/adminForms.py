from models import RawQuestionBank
from models import CompanyPosition
from django.forms import ModelForm
from django.db import connections
from django import forms
import collections
import logging

logger = logging.getLogger(__name__)

# UTILITY CHOICE WIDGET FOR DYNAMIC CHOICES


class DynamicChoiceField(forms.ChoiceField):
    def valid_value(self, value):
        return True


class signUpForm (forms.Form):
    username = forms.CharField(label='User Name')
    password = forms.CharField(label='Password',
                               widget=forms.PasswordInput)
    firstName = forms.CharField(label='First Name')
    lastName = forms.CharField(label='Last Name')
    email = forms.CharField(label='Email')
    phone = forms.CharField(label='Phone #', required=False)
    ianatimezone = forms.CharField(label='IANA TimeZone')


class loginForm (forms.Form):
    username = forms.CharField(label='User Name')
    password = forms.CharField(label='Password',
                               widget=forms.PasswordInput)


class addCompanyForm (forms.Form):
    companyName = forms.CharField(label='Company Name')
    positionName = forms.CharField(label='Position Name')
    minQuestions = forms.CharField(label='Minimum Questions In Test',
                                   initial='3')
    minDuration = forms.CharField(label='Minimum Test Duration (in mins)',
                                  initial='30')
    minQPerPool = forms.CharField(label='Minimum Questions Per Pool',
                                  initial='50')
    maxPools = forms.CharField(label='Maximum Number of Pools',
                               initial='6')
    poolIncrementCount = forms.CharField(label='Pool Increment Count',
                                         initial='50')


class editPositionForm(forms.Form):

    def __init__(self, *args, **kwargs):
        companyPositionObj = None
        if "companyPositionObj" in kwargs:
            companyPositionObj = kwargs.pop("companyPositionObj")
        super(editPositionForm, self).__init__(*args, **kwargs)
        if companyPositionObj:
            self.fields["companyName"].initial = companyPositionObj.\
                companyname
            self.fields["positionName"].initial = companyPositionObj.\
                positionname
            self.fields["minQuestions"].initial = companyPositionObj.\
                minquestions
            self.fields["minDuration"].initial = companyPositionObj.\
                minduration
            self.fields["minQPerPool"].initial = companyPositionObj.\
                minqperpool
            self.fields["maxPools"].initial = companyPositionObj.\
                maxpools
            self.fields["poolIncrementCount"].initial = companyPositionObj.\
                poolincrementcount
            self.fields["poolCount"].initial = companyPositionObj.\
                poolcount
            self.fields["currentPool"].initial = companyPositionObj.\
                curpool

    companyName = forms.CharField(
        label='Company Name',
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    positionName = forms.CharField(
        label='Position Name',
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    minQuestions = forms.CharField(label='Minimum Questions In Test')
    minDuration = forms.CharField(label='Minimum Test Duration (in mins)')
    minQPerPool = forms.CharField(label='Minimum Questions Per Pool')
    maxPools = forms.CharField(label='Maximum Number of Pools')
    poolIncrementCount = forms.CharField(label='Pool Increment Count')
    poolCount = forms.CharField(label='Current pool count')
    currentPool = forms.CharField(label='Current Active Pool')


class addPositionForm (forms.Form):

    def __init__(self, *args, **kwargs):
        super(addPositionForm, self).__init__(*args, **kwargs)
        cursor = connections["cassandra"].cursor()
        companies = cursor.execute("""
            SELECT DISTINCT companyname
            FROM company_position
            """)
        companyNames = map(lambda x: (x['companyname'], x['companyname']),
                           companies)
        cursor.close()
        self.fields['companyName'].choices = tuple(companyNames)

    companyName = DynamicChoiceField(label='Company Name')
    positionName = forms.CharField(label='Position Name')
    minQuestions = forms.CharField(label='Minimum Questions In Test',
                                   initial='3')
    minDuration = forms.CharField(label='Minimum Test Duration (in mins)',
                                  initial='30')
    minQPerPool = forms.CharField(label='Minimum Questions Per Pool',
                                  initial='50')
    maxPools = forms.CharField(label='Maximum Number of Pools',
                               initial='6')
    poolIncrementCount = forms.CharField(label='Pool Increment Count',
                                         initial='50')


class addQuestionForm (forms.Form):

    def __init__(self, *args, **kwargs):
        companyName = None
        if 'companyName' in kwargs:
            companyName = kwargs.pop('companyName')
        super(addQuestionForm, self).__init__(*args, **kwargs)
        if companyName:
            companies = CompanyPosition.objects.filter(companyname=companyName)
            positions = []
            for company in companies:
                positions.append((company.positionname, company.positionname))
            self.fields['companyName'].initial = companyName
            self.fields['positionName'].choices = positions

    companyName = forms.CharField(widget=forms.HiddenInput)
    positionName = DynamicChoiceField(label='Position Name')
    question = forms.CharField(label='Question', widget=forms.Textarea)
    questionType = forms.ChoiceField(label='Question Type',
                                     choices=[
                                      ('1', 'Multiple Choice Single Answer'),
                                      ('2', 'Multiple Choice Multiple Answer'),
                                      ('3', 'Descriptive Answer'),
                                      ('4', 'Program')])
    answer = forms.CharField(label='Answer', widget=forms.Textarea)
    choices = forms.CharField(label='Choices', required=False)
    input = forms.CharField(label='Input',
                            widget=forms.Textarea,
                            required=False)
    key = forms.CharField(label='Key', widget=forms.Textarea, required=False)
    timeToSolve = forms.CharField(label='Time to Solve', required=False)


class editQuestionForm (forms.Form):

    def __init__(self, *args, **kwargs):
        questionObj = None
        if 'question' in kwargs:
            questionObj = kwargs.pop('question')
        super(editQuestionForm, self).__init__(*args, **kwargs)
        if questionObj:
            self.fields['companyName'].initial = questionObj.companyname
            self.fields['positionName'].initial = questionObj.positionname
            self.fields['questionId'].initial = questionObj.questionid
            self.fields['question'].initial = questionObj.question
            self.fields['questionType'].initial = questionObj.questiontype
            self.fields['answer'].initial = questionObj.answer
            self.fields['choices'].initial = questionObj.choices or ""
            self.fields['input'].initial = questionObj.input
            self.fields['key'].initial = questionObj.key
            self.fields['timeToSolve'].initial = questionObj.timetosolve

    companyName = forms.CharField(widget=forms.HiddenInput)
    positionName = forms.CharField(widget=forms.HiddenInput)
    questionId = forms.CharField(widget=forms.HiddenInput)
    question = forms.CharField(label='Question',
                               widget=forms.Textarea(attrs={'rows': 10,
                                                            'cols': 140}))
    questionType = forms.ChoiceField(label='Question Type',
                                     choices=[
                                      ('1', 'Multiple Choice Single Answer'),
                                      ('2', 'Multiple Choice Multiple Answer'),
                                      ('3', 'Descriptive Answer'),
                                      ('4', 'Program')])
    answer = forms.CharField(label='Answer',
                             widget=forms.Textarea(attrs={'rows': 10,
                                                          'cols': 140}))
    choices = forms.CharField(label='Choices', required=False)
    input = forms.CharField(label='Input',
                            widget=forms.Textarea,
                            required=False)
    key = forms.CharField(label='Key', widget=forms.Textarea, required=False)
    timeToSolve = forms.CharField(label='Time to Solve', required=False)


class moderateQuestionForm(forms.Form):

    def __init__(self, *args, **kwds):
        questionVal = None
        questionTypeVal = None
        urlVal = None
        answerVal = None
        choicesVal = None
        inputVal = None
        keyVal = None
        timeToSolveVal = None
        companyName = None
        positionName = None
        questionId = None
        page = 1
        if 'page' in kwds:
            page = kwds.pop('page')
        if 'rawQuestion' in kwds:
            rawQuestion = kwds.pop('rawQuestion')
            questionVal = rawQuestion.question
            questionTypeVal = rawQuestion.questiontype
            urlVal = rawQuestion.url
            answerVal = rawQuestion.answer
            choicesVal = rawQuestion.choices
            inputVal = rawQuestion.input
            keyVal = rawQuestion.key
            timeToSolveVal = rawQuestion.timetosolve
            companyName = rawQuestion.companyname
            positionName = rawQuestion.positionname
            questionId = rawQuestion.questionid
        super(moderateQuestionForm, self).__init__(*args, **kwds)
        if questionVal:
            self.fields['question'].initial = questionVal
        if questionTypeVal:
            self.fields['questionType'].initial = questionTypeVal
        if urlVal:
            self.fields['url'].initial = urlVal
        if answerVal:
            self.fields['answer'].initial = answerVal
        if choicesVal:
            self.fields['choices'].initial = choicesVal
        if inputVal:
            self.fields['input'].initial = inputVal
        if keyVal:
            self.fields['key'].value = keyVal
        if timeToSolveVal:
            self.fields['timeToSolve'].initial = timeToSolveVal
        if companyName:
            self.fields['companyName'] = forms.CharField(
                                            initial=companyName,
                                            widget=forms.HiddenInput())
        if positionName:
            self.fields['positionName'] = forms.CharField(
                                            initial=positionName,
                                            widget=forms.HiddenInput())
        if questionId:
            self.fields['questionId'] = forms.CharField(
                                         initial=questionId,
                                         widget=forms.HiddenInput())
        if page:
            self.fields['page'] = forms.CharField(
                                   initial=page,
                                   widget=forms.HiddenInput())

    question = forms.CharField(label='Question',
                               widget=forms.Textarea(attrs={'rows': 10,
                                                            'cols': 140}))
    questionType = forms.ChoiceField(label='Question Type',
                                     choices=[
                                      ('1', 'Multiple Choice Single Answer'),
                                      ('2', 'Multiple Choice Multiple Answer'),
                                      ('3', 'Descriptive Answer'),
                                      ('4', 'Program')])
    url = forms.CharField(widget=forms.URLInput(attrs={'size': 120}))
    answer = forms.CharField(label='Answer',
                             widget=forms.Textarea(attrs={'rows': 10,
                                                          'cols': 140}))
    choices = forms.CharField(label='Choices', required=False)
    input = forms.CharField(label='Input',
                            widget=forms.Textarea,
                            required=False)
    key = forms.CharField(label='Key', widget=forms.Textarea, required=False)
    timeToSolve = forms.CharField(label='Time to Solve', required=False)
