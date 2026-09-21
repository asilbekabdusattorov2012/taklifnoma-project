from django.shortcuts import render
def Home_Page(request):
    return render(request,'Home_Page.html')
def biz_haqimizda(request):
    return render(request,'biz_haqimizda.html')
def boglanish(request):
    return render(request,'boglanish.html')
def toy(request):
    return render(request, 'toy.html')

def tugulgankun(request):
    return render(request, 'tugulgankun.html')

def yubley(request):
    return render(request, 'yubley.html')

def qiz(request):
    return render(request, 'qiz.html')

def eloshi(request):
    return render(request, 'elosh.html')

