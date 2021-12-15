import json
from datetime import date

from django.contrib.auth import login
from django.contrib.auth.backends import ModelBackend
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
        from wip.data import prod_data
        df = pd.read_excel('wip/Final Production Report Aug-Nov 2021.xlsx',
            'Data Sheet Aug-2021')
        new_header = df.iloc[1]  # grab the first row for the header
        df = df[2:]  # take the data less the header row
        df.columns = new_header  # set the header row as the df header
        df = df.loc[:, df.columns.notnull()]
        df['Date'] = df['Date'].astype(str)
        mask = df.sort_values(by=['Date'], ascending=False)
        mask = df[(df['Date'] == "2021-11-01 00:00:00")]
        columns = mask.columns.to_list()
        cols = {
            s: s.upper().replace("%", "").strip().replace(".", "").replace("\n",
                "").replace("/", "_") for s in columns}
        mask.rename(columns=cols, inplace=True)
        mc_yest = mask.groupby(['M_C NO'])['OEE','REJ'].mean().reset_index()
        mc_yest = mc_yest.to_dict(orient='records')
        oee_rej_mc = {k.get('M_C NO'):{'oee':k.get('OEE'),'rej':k.get('REJ')} for k in mc_yest}
        print(oee_rej_mc)
        pp = prod_data[0]
        machines  = {'data':{'B1':'Working',
                             'B2':'Thickness issue',
                             'L1':'Working',
                             'L2':'Mold change',
                             'INJ': 'Working',
                             'INJ1': 'No plan from PPC',
                             'LZR': 'No plan from PPC',
                             'LZ1': 'Working',
                             'P1': 'Working',
                              'PC1':'Working',
                              'PR1':'Working',
                              'Recycle': 'Working',
                              'WR1':'Working',
                             'WR2':'Working'},
                            "yesterday":oee_rej_mc
                     }
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
        data2show = {'oee':pp.get('OEE'),'plan-vs-actual':pp.get('PLAN VS ACTUAL ACHIEVEMENT'),
               'sku':pp.get('SKU'),"machine":pp.get('M/C NO')
        }
        yester = date.today() - timedelta(days=1)
        context={'data':shift_list,
                 'date':date.today(),
                 'machines':machines,
                 'yester':yester,
                 }
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
        print(data)
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
                color_ach = "green"
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

    elif item =="bottle":
        bottle  =[]
        for i in range(len(dates_)):
            bottle_d = {}
            achieved = random.randint(5000, 5500)
            ppc = random.randint(5200,5600)
            reject = round(random.uniform(0.5, 3.5),1)
            if achieved >ppc:
                color_ach = "green"
            else: color_ach ="#b94e48"
            if reject > 2.5:
                color_rej = "#b94e48"
            else: color_rej="green"
            bottle_d.update({'plan':ppc,'ach':achieved,'rej':reject,
                             'color_rej':color_rej,'color_ach':color_ach})
            bottle.append(bottle_d)
        context.update(data=bottle)
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


def demo_prod_report(request):

    return render(request, 'prod_report.html')
