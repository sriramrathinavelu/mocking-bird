from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^home.html$', views.home, name='home'),
    url(r'^login.html', views.login, name='login'),
    url(r'^logout.html', views.logout, name='logout'),
    url(r'^signup.html', views.signup, name='signup'),
    url(r'^test.html', views.test, name='test'),
    url(r'^savedTests.html', views.savedTests, name='savedTest'),
    url(r'^result.html', views.result, name='result'),
    url(r'^createtest.html', views.createTest, name='createTest'),
    url(r'^advancedtest.html', views.advancedTest, name='advancedTest'),
    url(r'^history.html', views.viewHistory, name='viewHistory'),
    url(r'^favouriteQuestions.html', views.viewFavouriteQuestions, name='viewFavouriteQuestions'),
    url(r'^favQuestion.html', views.viewFavouriteQuestion, name='viewFavouriteQuestion'),
    url(r'^schedTests.html', views.schedTests, name='scheduledTest'),
    url(r'^countdown.html', views.countDown, name='countdown'),
    url(r'^congrats.html', views.congrats, name='congrats'),
    url(r'^notVerified.html', views.notVerified, name='notVerified'),
]
