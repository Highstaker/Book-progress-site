from django.conf.urls import url

from . import views
from .api import api_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^index\.html$', views.index, name='index'),
    url(r'^book/$', views.book_choice, name='Book selection'),
    url(r'^book/(?P<book_id>[0-9]+)/$', views.book_stats, name='Book stats'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': "/"}, name='logout'),
    url(r'^api1/book/(?P<book_id>[0-9]+)/$', api_views.apiBookPages, name='API. Book Pages'),
    url(r'^api1/book/(?P<book_id>[0-9]+)/page/(?P<page_id>[0-9]+)/set_page_property$',api_views.apiTogglePageProperty,
        name='API. Set page property'),
]
