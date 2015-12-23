from django.conf.urls import url
from . import views

app_name = 'spaces'
urlpatterns = [
    url(r'^s/account/login$', views.LoginView.as_view(), name='login'),

    url(
        r'^_edit_/(?P<path>.*)?$',
        views.DocUpdateView.as_view(), name='document_edit'),
    url(
        r'^_add_/(?P<path>.*)?$',
        views.DocCreateView.as_view(), name='document_create'),
    url(
        r'^_delete_/(?P<pk>.*)?$',
        views.DocDeleteView.as_view(), name='document_delete'),
    url(
        r'^_revision_/(?P<pk>.*)?$',
        views.RevisionView.as_view(), name='document_revision'),
    url(
        r'^_info_/(?P<path>.*)?$',
        views.DocInfoView.as_view(), name='document_info'),
    url(
        r'^(?P<path>.*)$',
        views.DocDetailView.as_view(), name='document'),
]
