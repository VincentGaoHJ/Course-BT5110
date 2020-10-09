from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index),
    path('inventory/', views.inventory),
    path('new_product/', views.new_product),
    path('transaction/', views.transaction),
    path('operation/', views.operation),
]
