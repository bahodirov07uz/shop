from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name =  "asic"
urlpatterns = [
    path('', views.HomeView.as_view(), name="home"),
    path('catalog/', views.CatalogView.as_view(), name="catalog"),
    path('profile/', views.profile_view, name="profile"),
    path('detail/<int:pk>/', views.ProductDetailView.as_view(), name="detail"),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('buy-cart/add/<int:product_id>/', views.add_cart_buy, name='add_buy'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/order/', views.cart_order, name='cart_order'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('checkout/', views.checkout, name='checkout'),
    path('about/', views.AboutPage.as_view(), name='about'),

    #password reset
    path('reset_password/', auth_views.PasswordResetView.as_view(), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
