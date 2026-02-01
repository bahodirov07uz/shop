from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

app_name =  "asic"
urlpatterns = [
    path('', views.HomeView.as_view(), name="home"),
    path('catalog/', views.CatalogView.as_view(), name="catalog"),
    path('profile/', views.profile_view, name="profile"),
    path('detail/<int:pk>/', views.ProductDetailView.as_view(), name="detail"),
    path('order-cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('cart/add/<int:variant_id>/', views.add_to_cart, name='add_to_cart'),
    path('buy-cart/add/<int:variant_id>/', views.add_cart_buy, name='add_buy'),
    path('cart/remove/<int:variant_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('checkout/', views.checkout, name='checkout'),
    path('about/', views.AboutPage.as_view(), name='about'),
    path('privacy/', views.privacy, name='privacy'),
    path('payment-deliever/', views.paymentview, name='pay_deliever'),
    path('orders/', views.order_list, name='order_list'),
    path('cart/update/<int:variant_id>/', views.update_cart_quantity, name='update_cart_quantity'),    

    #password reset
    path('reset_password/', auth_views.PasswordResetView.as_view(), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('<slug:slug>/', views.static_page_view, name='static_page'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
