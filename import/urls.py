from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^reset_database$', views.reset_database, name='reset_database'),
]
