from django.conf.urls import url
from . import views

RESERVED_ROOT_URLS = [
    'login',
    'user',
    's',
    'settings',
    'reports',
    'admin'
]

app_name = 'spaces'
urlpatterns = [
    url(r'^login$', views.LoginView.as_view(), name='login'),
    url(r'^user/(?P<username>)/(?P<uri>.*)$', views.UserDocView.as_view(), name='user_doc'),
    url(r'^(?P<uri>.*)$', views.DocView.as_view(), name='space_doc')
]
