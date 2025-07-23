from django.shortcuts import render,redirect
from django.views.generic import TemplateView,DetailView,ListView
from .models import Product

class HomeView(ListView):
    template_name = "index.html"
    model = Product
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()[:3]
        return context
    
class CatalogView(TemplateView):
    template_name = "catalog.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        return context
class ProductDetailView(DetailView):
    model = Product
    template_name = "detail.html"
    context_object_name = 'product'