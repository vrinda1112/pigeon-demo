from django.shortcuts import render


def prod_sheet_input(request):
    print(request)
    return render(request,'production_sheet_form.html')