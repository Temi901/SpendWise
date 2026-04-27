from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add/', views.add_transaction, name='add_transaction'),
    path('delete/<int:pk>/', views.delete_transaction, name='delete_transaction'),
    path('edit/<int:pk>/', views.edit_transaction, name='edit_transaction'),
    path('budget/add/', views.add_budget, name='add_budget'),
    path('budget/delete/<int:pk>/', views.delete_budget, name='delete_budget'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
]