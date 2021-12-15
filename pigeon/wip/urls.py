from django.conf.urls import url
from django.urls import path, include
from django.urls import re_path
from wip.views import Login,Homepage, Reports,lim_checklist_report,\
    ppc_view, demo_prod_report, demo_prod_report_ajax
from wip.input_forms import *
urlpatterns = [
    # TelePro Api Starts Here
    path('login/', Login.as_view(), name='login'),
    path('',Homepage.as_view(),name="home"),
    path('checklist_report/', Reports.as_view()),
    path('lim_checklist_report/', lim_checklist_report),
    path('production_sheet_form/',prod_sheet_input),
    path('ppc_view/<slug:item>',ppc_view),
    path('prod_report_ajax',demo_prod_report_ajax),
    path('prod_report/',demo_prod_report),
]