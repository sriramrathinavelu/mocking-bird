from django.conf.urls import url
from . import mentorViews

urlpatterns = [
    url(r'^$', mentorViews.home, name='mentorHome'),
    url(r'^home.html', mentorViews.home, name='mentorHome'),
    url(r'^favourite.html', mentorViews.favourite, name='mentorFavourite'),
    url(r'^search.html', mentorViews.search, name='mentorSearch'),
    url(r'^evaluate.html', mentorViews.evaluateTest, name='evaluateTest'),
]
