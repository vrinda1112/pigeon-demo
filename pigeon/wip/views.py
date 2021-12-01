import json

from django.contrib.auth import login
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
import pandas as pd
from wip.models import LIMChecklist, LIMParameters

class CaseInsensitiveModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(username__iexact=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

class Login(View):
    def get(self,request):
        return render(request,'login.html')
    def post(self,request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = CaseInsensitiveModelBackend()
        user = user_obj.authenticate(request,
                    username=email,
                    password=password)

        next_url = '/'
        if user:
            login(request, user)
            return redirect(next_url)
        else:
            return json.dumps({'msg':'wrong creds'})

class Homepage(View):
    def get(self,request):
        return render(request,'index.html')

class Reports(View):
    def get(self,request):
        report_type = request.GET.get('rtype')
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        if report_type == "lim_check":
            print(request)
        return render(request,'lim_checklist.html')


def lim_checklist_report(request):
    rtype = request.GET.get('rtype')
    if rtype == "lim_check":
        df = pd.read_csv('wip/checklist.csv')
        data =df.to_dict(orient='records')
        response = {'data': data}
        print(response)
        return JsonResponse(response)


