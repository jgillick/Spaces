from django.conf.urls import url
from . import views, api_views

app_name = 'spaces'
urlpatterns = [

    #
    # API Views
    #
    # url(
    #     r'^api/v1/spaces/$',
    #     api_views.SpaceList.as_view(),
    #     name='api_spaces'),
    # url(
    #     r'^api/v1/spaces/(?P<path>.*)$',
    #     api_views.SpaceDetail.as_view(),
    #     name='api_space'),
    # url(
    #     r'^api/v1/documents/(?P<path>.*)$',
    #     api_views.DocumentDetail.as_view(),
    #     name='api_document'),

    #
    # Web Views
    #
    url(r'^s/login$', views.LoginView.as_view(), name='login'),
    url(
        r'^s/logout$', 'django.contrib.auth.views.logout',
        {'next_page': 'spaces:root'}, name='logout'),

    url(r's/upload', views.file_upload_view, name='file_upload'),

    # Document views
    url(r'^$', views.DocDetailView.as_view(), {'path': ''}, name='root'),

    url(r'^_edit_/(?P<path>.*)?$',
        views.DocUpdateView.as_view(), name='document_edit'),
    url(r'^_add_/(?P<path>.*)?$',
        views.DocCreateView.as_view(), name='document_create'),
    url(r'^_delete_/(?P<pk>.*)?$',
        views.DocDeleteView.as_view(), name='document_delete'),
    url(r'^_revision_/(?P<pk>.*)?$',
        views.RevisionView.as_view(), name='document_revision'),
    url(r'^_info_/(?P<path>.*)?$',
        views.DocInfoView.as_view(), name='document_info'),
    url(r'^(?P<path>.*)$',
        views.DocDetailView.as_view(), name='document'),
]
