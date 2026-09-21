from django.contrib import admin
from django.urls import path
from . import view
from toylar import views as toy_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', view.Home_Page, name='home'),
    path('biz_haqimizda/', view.biz_haqimizda, name='biz_haqimizda'),
    path('boglanish/', view.boglanish, name='boglanish'),
    path('toy/', toy_views.toy, name='toy'),
    path('tugulgankun/', toy_views.tugulgankun, name='tugulgankun'),
    path('yubley/', toy_views.yubley, name='Yubley'),
    path('Qiz/', toy_views.qiz, name='Qiz'),
    path('eloshi/', toy_views.eloshi, name='eloshi'),
    path('buyurtma/', toy_views.buyurtma, name='buyurtma'),
]
