from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^index\.html$', views.index, name='index'),
    url(r'^book/$', views.book_choice, name='Book selection'),
    url(r'^book/(?P<book_id>[0-9]+)/$', views.book_stats, name='Book stats'),
]
