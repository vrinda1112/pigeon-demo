import json
from datetime import date

from django.contrib.auth import login
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
import pandas as pd
from datetime import datetime
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
        context={'date':date.today()}
        return render(request,'login.html',context=context)
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
        prod_dict_nipple_a = {"shift":"a","t_p":5763,'t_gp':4700,'setup':343,'qc_samples':40,
                            'rm_consumption':'34kg','prod':'nipple'}
        prod_dict_bottle_a = {"shift":"a","t_p": 570, 't_gp': 470, 'setup': 50,
                            'qc_samples': 50,'prod':'bottle',
                            'rm_consumption': '78kg', }
        prod_dict_nipple_b = {"shift":"b","t_p": 5763, 't_gp': 4700, 'setup': 343,
                              'qc_samples': 40,'prod':'nipple',
                              'rm_consumption': '34kg', }
        prod_dict_bottle_b = {"shift":"b","t_p": 570, 't_gp': 470, 'setup': 50,
                              'qc_samples': 50,'prod':'bottle',
                              'rm_consumption': '78kg', }
        shift_dict = {'a':{'nipple':prod_dict_nipple_a,'bottle':prod_dict_bottle_a},
                        'b':{'nipple':prod_dict_nipple_b,'bottle':prod_dict_bottle_b}
                      }
        shift_list = [prod_dict_bottle_b,prod_dict_bottle_a,
                      prod_dict_nipple_a,prod_dict_nipple_b]
        context={'data':shift_list,'date':date.today()}
        return render(request,'index.html',context=context)

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
        return JsonResponse(response)


def ppc_view(request,item):
    import calendar
    import datetime
    import random
    now = datetime.datetime.now()
    dates_ = calendar.monthrange(now.year, now.month)[1]
    date1 = date.today().replace(day=1).strftime("%A")
    seven_days = [date.today().replace(day=n + 1).strftime("%A") for n in
                  range(7)]
    print(seven_days)
    dates_ = [i for i in range(dates_ + 1) if i != 0]
    context = {'dates': dates_, 'days': seven_days}
    if item == "nipple":
        nipple = []
        for i in range(len(dates_)):
            nipple_d = {}
            achieved = random.randint(5000, 5500)
            ppc = random.randint(5200,5600)
            reject = round(random.uniform(0.5, 3.5),1)
            if achieved > ppc:
                color_ach = "#007474"
            else:
                color_ach = "#b94e48"
            if reject > 1.5:
                color_rej = "#b94e48"
            else:
                color_rej = "#007474"
            nipple_d.update({'plan':ppc,'ach':achieved,'rej':reject,
                             'color_rej':color_rej,'color_ach':color_ach})
            nipple.append(nipple_d)
        context.update(data=nipple)

    elif item =="bottle":
        bottle  =[]
        for i in range(len(dates_)):
            bottle_d = {}
            achieved = random.randint(5000, 5500)
            ppc = random.randint(5200,5600)
            reject = round(random.uniform(0.5, 3.5),1)
            if achieved >ppc:
                color_ach = "#007474"
            else: color_ach ="#b94e48"
            if reject > 2.5:
                color_rej = "#b94e48"
            else: color_rej="#007474"
            bottle_d.update({'plan':ppc,'ach':achieved,'rej':reject,
                             'color_rej':color_rej,'color_ach':color_ach})
            bottle.append(bottle_d)
        context.update(data=bottle)
    return render(request,'ppc.html', context)

def demo_prod_report_ajax(request):
    if request.method == "GET":
        df = pd.read_excel('wip/Final Production Report Aug-Nov 2021.xlsx','Data Sheet Aug-2021')
        new_header = df.iloc[1]  # grab the first row for the header
        df = df[2:]  # take the data less the header row
        df.columns = new_header  # set the header row as the df header
        print(df.columns.to_list())
        df = df.loc[:, df.columns.notnull()]
        mask = df[(df['Month'] == 11)]
        json_data = mask.to_dict(orient='records')
        return JsonResponse(json_data, safe=False)

def demo_prod_report(request):
    return render(request, 'prod_report.html')
