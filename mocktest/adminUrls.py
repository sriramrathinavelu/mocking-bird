from django.conf.urls import url
from . import adminViews

urlpatterns = [
    url(r'^addCompany.html$', adminViews.addCompany),
    url(r'^addPosition.html$', adminViews.addPosition),
    url(r'^editPosition.html$', adminViews.editPosition),
    url(r'^addQuestion.html$', adminViews.addQuestion),
    url(r'^editQuestion.html$', adminViews.editQuestion),
    url(r'^moderateQuestionTable.html$', adminViews.moderateQuestionTable),
    url(r'^moderateQuestion.html$', adminViews.moderateQuestion),
    url(r'^home.html$', adminViews.home),
    url(r'^error.html$', adminViews.error),
    url(r'^moderatorLogin.html$', adminViews.login),
    url(r'^moderatorLogout.html$', adminViews.logout),
    url(r'^moderatorSignUp.html$', adminViews.signup),
    url(r'^verification.html$', adminViews.verification),
    url(r'^moderateMentorsTable.html$', adminViews.moderateMentorsTable),
    url(r'^moderateMentor.html$', adminViews.moderateMentor),
    url(r'^addModeratorsTable.html$', adminViews.addModeratorsTable),
    url(r'^addModerator.html$', adminViews.addModerator),
    url(r'^acceptMentor.html$', adminViews.acceptMentor),
]
