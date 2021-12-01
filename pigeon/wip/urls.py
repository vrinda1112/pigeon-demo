from django.conf.urls import url
from django.urls import path, include
from django.urls import re_path
from wip.views import Login,Homepage, Reports,lim_checklist_report

urlpatterns = [
    # TelePro Api Starts Here
    path('login/', Login.as_view(), name='login'),
    path('',Homepage.as_view(),name="home"),
    path('report/', Reports.as_view()),
    path('report/lim_checklist_report/', lim_checklist_report),
]