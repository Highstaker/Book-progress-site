from django.conf.urls import url

from . import views
from .api import api_views
from django.contrib.auth import views as auth_views

app_name = 'myreprogress'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^index\.html$', views.index, name='index'),
    url(r'^book/$', views.BookChoiceView.as_view(), name='Book selection'),

    url(r'^book/(?P<book_id>[0-9]+)/$', views.BookStatsView.as_view(), name='Book stats'),
    url(r'^book/(?P<book_slug>[a-zA-Z0-9\-]+)/$', views.BookStatsView.as_view(), name='Book stats'),  # access via slug

    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': "/"}, name='logout'),

    url(r'^api1/book/(?P<book_id>[0-9]+)/$', api_views.apiBookPages, name='API. Book Pages'),
    url(r'^api1/book/(?P<book_id>[0-9]+)/page/(?P<page_number>[0-9]+)/set_page_property$', api_views.apiTogglePageProperty,
        name='API. Set page property'),
    url(r'^api1/book/(?P<book_id>[0-9]+)/add_pages$', api_views.apiInsertPages,
        name='API. Add pages to book'),
    url(r'^api1/book/(?P<book_id>[0-9]+)/validate_pages$', api_views.apiValidatePages,
        name='API. Validate page numbers'),
    url(r'^api1/book/(?P<book_id>[0-9]+)/delete_pages$', api_views.apiDeletePages,
        name='API. Delete pages'),

]
