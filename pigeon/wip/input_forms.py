from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import json

@login_required
def prod_sheet_input(request):
    if request.method=="GET":
        return render(request,'production_sheet_form.html')

def prod_sheet_input_ajax(request):
    if request.method== "POST":
        print(request)
    return json.dumps({})

@login_required
def nipple_prod_sheet(request):
    print(request)
    return render(request,'nipple_prod_sheet2.html')