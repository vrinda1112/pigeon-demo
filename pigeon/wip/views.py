import json
from datetime import date

from django.template.context_processors import csrf
from django.utils.decorators import method_decorator
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
import pandas as pd
from datetime import timedelta
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
        user = User.objects.get(email=email)
        user_obj = authenticate(request, username='demouser', password=password)
        # user = user_obj.authenticate(request,
        #             username=email,
        #             password=password)

        next_url = '/'
        if user:
            login(request, user)
            return redirect(next_url)
        else:
            return json.dumps({'msg':'wrong creds'})

def logoutview(request):
    """Show the login page.
    If 'next' is a URL parameter, add its value to the context.  (We're
    mimicking the standard behavior of the django login auth view.)
    """

    try:
        print("logged out")
    except:
        pass
    logout(request)
    return redirect('/')


class Homepage(View):
    @method_decorator(login_required)
    def get(self,request):
        from wip.data import prod_data
        # from wip.data import bar_graph_month
        process =  {'B1':{'plan':2503,'item':'bottle molded',
                                  'pp-out':2250,'oee':88, 'actual':2650,
                          'rej':2.2,'color':"green",'plan_today':4000, 'actual_till_now':2300},
                     'B2':{'plan':2334, 'item':'bottle molded',
                          'pp-out':2312,'oee':77,'month':'nov', 'actual':2436, 'rej':0.3,
                           'color':'green','plan_today':4233, 'actual_till_now':2323},
                     "PR1":{'plan':4400, 'item':'bottle printed',
                          'pp-out':691,'oee':94,'month':'nov', 'actual':4199, 'rej':1.2,
                            'color':'green','plan_today':'No plan from PPC', 'actual_till_now':'0'},
                     'L1':{'plan':4815, 'item':'nipple molded',
                          'pp-out':2220,'oee':50,'month':'nov', 'actual':2346, 'rej':1.4,
                           'color':'red','plan_today':4003, 'actual_till_now':1323},
                     'L2':{'plan':6745, 'item':'nipple molded',
                          'pp-out':5562,'oee':90,'month':'nov', 'actual':5000, 'rej':2.2,'color':'red',
                           'plan_today':5234, 'actual_till_now':1723},
                     "PC1": {'plan':5500, 'item':'nipple postcure',
                          'pp-out':5572,'oee':98,'month':'nov', 'actual':6003, 'rej':3.3,'color':'green',
                             'plan_today':5403, 'actual_till_now':3323},
                     'INJ1': {'plan':1800, 'item':'cap molded',
                          'pp-out':1674,'oee':89.3,'month':'nov', 'actual':1860,  'rej':0.0,'color':'green',
                              'plan_today':6403, 'actual_till_now':2023},
                     'LZ1': {'plan':3462, 'item':'nipple lazer  marking',
                          'pp-out':3421,'oee':98.12,'month':'nov', 'actual':4000,'rej':1.3,'color':'red',
                             'plan_today':3200, 'actual_till_now':1023},
                      'WR1':{'plan':6003, 'item':'nipple wrap printed',
                          'pp-out':5412,'oee':91.32,'month':'nov', 'actual':5409,'rej':0.3,'color':'red',
                             'plan_today':'No plan from PPC', 'actual_till_now':'0'},
                     'WR2':{'plan':4500, 'item':'nipple wrap printed',
                          'pp-out':4592,'oee':78.34,'month':'nov', 'actual':4600,'rej':1.32,'color':'green',
                            'plan_today':4500, 'actual_till_now':1200},
                     'WR':{'plan':3450, 'item':'nipple wrap printed',
                          'pp-out':3300,'oee':97.32,'month':'nov', 'actual':3330,'rej':2.3,'color':'red',
                           'plan_today':2303, 'actual_till_now':900},
                     }
        today_data = {'B1': {'plan': 4000, 'actual': 2300},
                      'B2': {'plan': 'No plan from PPC'},
                      'L1': {'plan': 4300, 'actual': 1300},
                      'L2': {'plan': 2310, 'actual': 1231},
                      "PR1": {'plan': 3411, 'actual': 1211},
                      'INJ1': {'plan': "np plan from PPC"},
                      'LZR': {'plan': 6523, 'actual': 3411},
                      'LZ1': {'plan': 3234, 'actual': 987},
                      'WR1': {'plan': 4521, 'actual': 313},
                      'WR2': {'plan': 5622, 'actual': 3211},
                      'WR': {'plan': 5200, 'actual': 3412}
                      }
        yester = date.today() - timedelta(days=1)
        context={'data_today':today_data,
                 'date':date.today(),
                 'machines':process,
                 'yester':yester,

                 }
        return render(request,'index.html',context=context)

class Reports(View):


    @method_decorator(login_required)
    def get(self,request):
        report_type = request.GET.get('rtype')
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        if report_type == "lim_check":
            print(request)
        return render(request,'lim_checklist.html')

@login_required
def lim_checklist_report(request):
    rtype = request.GET.get('rtype')
    if rtype == "lim_check":
        df = pd.read_csv('wip/checklist.csv')
        data =df.to_dict(orient='records')
        print(data)
        response = {'data': data}
        return JsonResponse(response)

@login_required
def ppc_view(request,item):
    import calendar
    import datetime
    import random
    now = datetime.datetime.now()
    dates_ = calendar.monthrange(now.year, now.month)[1]
    date1 = date.today().replace(day=1).strftime("%A")
    seven_days = [date.today().replace(day=n + 1).strftime("%A") for n in
                  range(7)]
    dates_ = [i for i in range(dates_ + 1) if i != 0]
    context = {'dates': dates_, 'days': seven_days}
    nipple = []
    for i in range(len(dates_)):
        nipple_d = {}
        achieved = random.randint(7200, 8300)
        ppc = random.randint(7000,7800)
        reject = round(random.uniform(0.5, 3.5),1)
        if achieved > ppc:
            color_ach = "#2e8b57"
        else:
            color_ach = "#b94e48"
        if reject > 1.5:
            color_rej = "#b94e48"
        else:
            color_rej = "green"
        nipple_d.update({'plan':ppc,'ach':achieved,'rej':reject,
                         'color_rej':color_rej,'color_ach':color_ach})
        nipple.append(nipple_d)
    context.update(data=nipple)

    return render(request,'ppc.html', context)


def demo_prod_report_ajax(request):
    if request.method == "GET":
        endDate = request.GET.get('endDate')
        fromDate = request.GET.get('fromDate')
        print(endDate, fromDate)
        df = pd.read_excel('wip/Final Production Report Aug-Nov 2021.xlsx','Data Sheet Aug-2021')
        new_header = df.iloc[1]  # grab the first row for the header
        df = df[2:]  # take the data less the header row
        df.columns = new_header  # set the header row as the df header
        df = df.loc[:, df.columns.notnull()]
        df['Date'] = df['Date'].astype(str)
        mask = df.sort_values(by=['Date'], ascending=False)
        if endDate and fromDate:
            end_ = datetime.strptime(endDate, "%d%m%Y%H%M")
            from_ = datetime.strptime(fromDate, "%d%m%Y%H%M")
            endDate = datetime.strftime(end_, "%Y-%m-%d %H:%M:%S")
            fromDate = datetime.strftime(from_, "%Y-%m-%d %H:%M:%S")
            print(fromDate,endDate)
            mask = df[(df['Date'] >= fromDate) & (df['Date'] <= endDate)]
            print(mask.head())
        else:
            mask = df[df['Month'] == 11]

        columns = mask.columns.to_list()
        cols = {s:s.upper().replace("%","").strip().replace(".","").replace("\n", "") for s in columns}
        mask.rename(columns=cols,inplace=True)

        cols = ['MATERIAL YIELD', 'REJ', 'TOTAL BRAEKDOWN HRS']
        mask[cols] = mask[cols].apply(pd.to_numeric, errors='coerce', axis=1)
        mask = mask.round(2)
        mask.fillna("-", inplace=True)
        mask = mask.round(2)
        json_data = mask.to_dict(orient='records')

        return JsonResponse(
            {
                'data': json_data,
                "draw": 1,
                "recordsTotal": len(json_data),
                "recordsFiltered": len(json_data),
                "cols":cols
            }
        )

@login_required
def demo_prod_report(request):
    return render(request, 'prod_report.html')
