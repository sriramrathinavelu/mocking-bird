from django.conf.urls import url
from . import views, ajaxUtils

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^home.html$', views.home, name='home'),
	url(r'^login.html', views.login, name='login'),
	url(r'^logout.html', views.logout, name='logout'),
	url(r'^signup.html', views.signup, name='signup'),
	url(r'^test.html', views.test, name='test'),
	url(r'^savedTests.html', views.savedTests, name='savedTest'),
	url(r'^result.html', views.result, name='result'),
	url(r'^quicktest.html', views.createTest, name='createTest'),
	url(r'^history.html', views.viewHistory, name='viewHistory'),
]
