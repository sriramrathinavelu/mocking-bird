from django.conf.urls import url
from . import adminViews

urlpatterns = [
    url(r'addCompany.html$', adminViews.addCompany),
    url(r'addPosition.html$', adminViews.addPosition),
    url(r'addQuestion.html$', adminViews.addQuestion),
    url(r'editQuestion.html', adminViews.editQuestion),
	url(r'moderateQuestionTable.html', adminViews.moderateQuestionTable),
	url(r'moderateQuestion.html', adminViews.moderateQuestion),
	url(r'home.html$', adminViews.home),
	url(r'error.html$', adminViews.error),
]
