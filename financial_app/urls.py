# eeuezconsulting_app/financial_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs (custom views)
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'), # Use your custom logout view

    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Income URLs
    path('incomes/', views.income_list, name='income_list'),
    path('incomes/add/', views.add_income, name='add_income'),
    path('incomes/edit/<int:pk>/', views.edit_income, name='edit_income'),
    path('incomes/delete/<int:pk>/', views.delete_income, name='delete_income'),

    # Expense URLs
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.add_expense, name='add_expense'),
    path('expenses/edit/<int:pk>/', views.edit_expense, name='edit_expense'),
    path('expenses/delete/<int:pk>/', views.delete_expense, name='delete_expense'),

    # Project URLs
    path('projects/', views.project_list, name='project_list'),
    path('projects/add/', views.add_project, name='add_project'),
    path('projects/edit/<int:pk>/', views.edit_project, name='edit_project'),
    path('projects/delete/<int:pk>/', views.delete_project, name='delete_project'),
    path('complete-project/', views.complete_project, name='complete_project'), # NEW: URL for completing projects via AJAX

    # Recommendations & Education
    path('recommendations/', views.recommendations_list, name='recommendations_list'),
    path('education/', views.education_modules_list, name='education_modules_list'),
]