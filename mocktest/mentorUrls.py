from django.conf.urls import url
from . import mentorViews

urlpatterns = [
    url(r'^$', mentorViews.home, name='mentorHome'),
    url(r'^favourite.html', mentorViews.favourite, name='mentorFavourite'),
]
