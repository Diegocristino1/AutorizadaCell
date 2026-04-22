from django.urls import path

from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('produtos/', views.ProductListView.as_view(), name='product_list'),
    path(
        'categoria/<slug:slug>/',
        views.ProductListView.as_view(),
        name='category',
    ),
    path('produto/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('sobre/', views.SobreView.as_view(), name='sobre'),
    path('contato/', views.contato, name='contato'),
]
