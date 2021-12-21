from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def prod_sheet_input(request):
    print(request)
    return render(request,'production_sheet_form.html')

@login_required
def nipple_prod_sheet(request):
    print(request)
    return render(request,'nipple_prod_sheet2.html')