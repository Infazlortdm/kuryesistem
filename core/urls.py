from django.urls import path
from . import views

urlpatterns = [
    path('', views.anasayfa, name='anasayfa'),
    path('ekle/', views.siparis_ekle, name='siparis_ekle'),
    path('al/<int:id>/', views.siparis_al, name='siparis_al'),
    path('teslim/<int:id>/', views.siparis_teslim, name='siparis_teslim'),
    path('gunsonu/', views.gun_sonu, name='gun_sonu'),
]