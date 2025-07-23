from django.contrib import admin
from django.urls import path
from .views import HomeView,CatalogView,ProductDetailView

app_name =  "asic"
urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('catalog/', CatalogView.as_view(), name="catalog"),
    path('detail/<int:pk>/', ProductDetailView.as_view(), name="detail"),
    
]
