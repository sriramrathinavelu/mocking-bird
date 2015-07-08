from django.conf.urls import url
from . import ajaxUtils

urlpatterns = [
    url(r'^getPositions.html$', ajaxUtils.getPositions),
    url(r'^isUsernameValid.html$', ajaxUtils.isUsernameValid),
    url(r'^saveAnswer.html$', ajaxUtils.saveAnswer),
    url(r'^notifyTestStart.html$', ajaxUtils.notifyTestStart),
    url(r'^submitTest.html$', ajaxUtils.submitTest),
    url(r'^saveTest.html$', ajaxUtils.saveTest),
    url(r'^exitTest.html$', ajaxUtils.exitTest),
    url(r'^userTests.html$', ajaxUtils.getUserTests),
    url(r'^userSavedTests.html$', ajaxUtils.getUserSavedTests),
    url(r'^userSchedTests.html$', ajaxUtils.getUserSchedTests),
    url(r'^userCompany.html$', ajaxUtils.getUserCompany),
    url(r'^userPosition.html$', ajaxUtils.getUserPosition),
    url(r'^userCompanyTests.html$', ajaxUtils.getUserCompanyTests),
    url(r'^userPositionTests.html$', ajaxUtils.getUserPositionTests),
    url(r'^userCompanyFavourites.html$', ajaxUtils.getUserCompanyFavourites),
    url(r'^userPositionFavourites.html$', ajaxUtils.getUserPositionFavourites),
    url(r'^userCompanyPosition.html$', ajaxUtils.getUserCompanyPosition),
    url(r'^userPositionCompany.html$', ajaxUtils.getUserPositionCompany),
    url(r'^mentorTests.html$', ajaxUtils.getMentorTests),
    url(r'^mentorCompanyPosition.html$', ajaxUtils.getMentorCompanyPosition),
    url(r'^mentorPositionCompany.html$', ajaxUtils.getMentorPositionCompany),
    url(r'^evaluateTest.html$', ajaxUtils.evaluateTest),
    url(r'^saveComment.html$', ajaxUtils.saveComment),
    url(r'^saveEvaluationResult.html$', ajaxUtils.saveEvaluationResult),
    url(r'^cancelEvaluation.html$', ajaxUtils.cancelEvaluation),
    url(r'^vote.html$', ajaxUtils.updateUserQuestionInteraction),
    url(r'^mentorRequest.html$', ajaxUtils.mentorRequest)
]
