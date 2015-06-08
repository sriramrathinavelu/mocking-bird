from django.conf.urls import url
from . import ajaxUtils

urlpatterns = [
    url(r'^getPositions.html$', ajaxUtils.getPositions),
	url(r'^isUsernameValid.html$', ajaxUtils.isUsernameValid),
	url(r'^saveAnswer.html$', ajaxUtils.saveAnswer),
	url(r'^changeTestState.html$', ajaxUtils.changeTestState),
	url(r'^submitTest.html$', ajaxUtils.submitTest),
	url(r'^saveTest.html$', ajaxUtils.saveTest),
	url(r'^exitTest.html$', ajaxUtils.exitTest),
	url(r'^userTests.html$', ajaxUtils.getUserTests),
	url(r'^userSavedTests.html$', ajaxUtils.getUserSavedTests),
	url(r'^userCompany.html$', ajaxUtils.getUserCompany),
	url(r'^userPosition.html$', ajaxUtils.getUserPosition),
	url(r'^userCompanyTests.html$', ajaxUtils.getUserCompanyTests),
	url(r'^userPositionTests.html$', ajaxUtils.getUserPositionTests),
	url(r'^userCompanyPosition.html$', ajaxUtils.getUserCompanyPosition),
	url(r'^userPositionCompany.html$', ajaxUtils.getUserPositionCompany),
]
