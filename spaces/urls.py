from django.conf.urls import url
from . import views

app_name = 'spaces'
urlpatterns = [
    url(r'^s/account/login$', views.LoginView.as_view(), name='login'),
    # url(r'^user/(?P<username>)/(?P<uri>.*)$', views.UserDocView.as_view(), name='user_doc'),

    url(
        r'^_edit_/(?P<path>.*)?$',
        views.DocUpdate.as_view(), name='document_edit'),
    url(
        r'^_add_/(?P<path>.*)?$',
        views.DocCreate.as_view(), name='document_create'),
    url(
        r'^_delete_/(?P<pk>.*)?$',
        views.DocDelete.as_view(), name='document_delete'),
    url(
        r'^(?P<path>.*)$',
        views.DocView.as_view(), name='document'),
]
