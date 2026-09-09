from django.urls import path
from . import views

urlpatterns = [
    path('', views.toy, name='toy_catalog'),
    path('buyurtma/', views.buyurtma, name='buyurtma_catalog'),
]
