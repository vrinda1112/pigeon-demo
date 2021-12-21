from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def prod_sheet_input(request):
    print(request)
    return render(request,'nipple_prod_sheet.html')

@login_required
def nipple_prod_entry(request):
    return render(request,'nipple_prod_sheet.html')