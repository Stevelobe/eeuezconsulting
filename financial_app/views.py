# eeuezconsulting_app/financial_app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth import login, logout # Import specific login/logout functions
from django.contrib.auth.forms import AuthenticationForm # Django's built-in login form
from django.http import JsonResponse # Import JsonResponse for AJAX replies
from django.views.decorators.http import require_POST # For enforcing POST requests on AJAX views
import json # For parsing JSON from request body

from .models import Income, Expense, Project, Recommendation, EducationModule
from .forms import IncomeForm, ExpenseForm, ProjectForm, CustomUserCreationForm # Import your forms

# --- Authentication Views ---

def register_view(request):
    """
    Handles user registration.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login') # Redirect to login page after registration
        else:
            messages.error(request, 'Error during registration. Please check your input.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form, 'title': 'Register'})

def login_view(request):
    """
    Handles user login.
    Uses Django's built-in AuthenticationForm.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user) # Log the user in
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard') # Redirect to dashboard after login
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form, 'title': 'Login'})

@login_required
def logout_view(request):
    """
    Handles user logout.
    """
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login') # Redirect to login page after logout

# --- Main Application Views ---

@login_required
def dashboard_view(request):
    """
    Displays the user's financial dashboard with summary, recent entries, projects, and recommendations.
    """
    # Fetch recent items
    user_incomes = Income.objects.filter(user=request.user).order_by('-date')[:5]
    user_expenses = Expense.objects.filter(user=request.user).order_by('-date')[:5]
    user_recommendations = Recommendation.objects.filter(user=request.user, is_read=False).order_by('-date_created')[:3]
    
    # Calculate financial summaries
    total_income = Income.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    net_balance = total_income - total_expense

    # --- Prepare Project Data for Dashboard ---
    # 1. Projects for the main 'Your Projects' table (uncompleted projects)
    user_projects_display = Project.objects.filter(user=request.user, is_completed=False).order_by('due_date')

    # 2. Projects for JavaScript (all projects, converted to JSON-serializable list of dicts)
    # This data will be used by the JavaScript for client-side logic like sorting for 'Most Valuable Projects'.
    all_user_projects_queryset = Project.objects.filter(user=request.user).order_by('due_date')
    projects_json_data = []
    for project in all_user_projects_queryset:
        projects_json_data.append({
            'id': project.id,
            'name': project.name,
            # Ensure amounts are floats for JS operations
            'target_amount': float(project.target_amount) if project.target_amount is not None else 0.0,
            'current_amount': float(project.current_amount) if project.current_amount is not None else 0.0,
            'is_completed': project.is_completed,
            'due_date': project.due_date.strftime('%Y-%m-%d') if project.due_date else None
        })

    # 3. Most Valuable Projects for direct template rendering (top 3 by target_amount, can include completed)
    most_valuable_projects_queryset = Project.objects.filter(user=request.user).order_by('-target_amount')[:3]
    most_valuable_projects_for_template = []
    for project in most_valuable_projects_queryset:
        most_valuable_projects_for_template.append({
            'id': project.id,
            'name': project.name,
            'target_amount': float(project.target_amount) if project.target_amount is not None else 0.0,
            'current_amount': float(project.current_amount) if project.current_amount is not None else 0.0,
            'is_completed': project.is_completed,
            'due_date': project.due_date.strftime('%Y-%m-%d') if project.due_date else None
        })


    context = {
        'user_incomes': user_incomes,
        'user_expenses': user_expenses,
        'user_projects': user_projects_display, # This is for the Django loop for the main table
        'projects_json_data': projects_json_data, # This is for the json_script tag
        'most_valuable_projects': most_valuable_projects_for_template, # This is for the specific section
        'user_recommendations': user_recommendations,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': net_balance,
    }
    return render(request, 'financial_app/dashboard.html', context)

# --- AJAX View to Complete a Project ---
@login_required
@require_POST # Ensure only POST requests are allowed
def complete_project(request):
    try:
        data = json.loads(request.body)
        project_id = data.get('project_id')
        
        if not project_id:
            return JsonResponse({'success': False, 'error': 'Project ID is required.'}, status=400)

        project = get_object_or_404(Project, pk=project_id, user=request.user)
        
        # Mark project as completed
        project.is_completed = True
        project.save()

        # Create an Income entry from the project's target/current amount
        # Decide whether to use target_amount or current_amount for income
        amount_to_add = project.target_amount if project.target_amount is not None else project.current_amount
        if amount_to_add is None: # Fallback if both are None
            amount_to_add = 0

        # Create an Income instance
        Income.objects.create(
            user=request.user,
            amount=amount_to_add,
            source=f"Project Completion: {project.name}",
            date=project.due_date if project.due_date else Income.objects.latest('date').date # Use due date or latest income date as fallback
        )
        
        return JsonResponse({'success': True, 'message': f'Project "{project.name}" completed and income updated.'})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON in request body.'}, status=400)
    except Project.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Project not found or not authorized.'}, status=404)
    except Exception as e:
        # Catch any other unexpected errors
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# --- Income Views (rest of your views remain the same) ---

@login_required
def income_list(request):
    """Displays a list of all income entries for the logged-in user."""
    incomes = Income.objects.filter(user=request.user).order_by('-date')
    context = {'incomes': incomes, 'title': 'My Incomes'}
    return render(request, 'financial_app/income_list.html', context)

@login_required
def add_income(request):
    """Handles adding a new income entry."""
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            messages.success(request, 'Income added successfully!')
            return redirect('income_list')
        else:
            messages.error(request, 'Error adding income. Please check your input.')
    else:
        form = IncomeForm()
    return render(request, 'financial_app/income_form.html', {'form': form, 'title': 'Add Income'})

@login_required
def edit_income(request, pk):
    """Handles editing an existing income entry."""
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            messages.success(request, 'Income updated successfully!')
            return redirect('income_list')
        else:
            messages.error(request, 'Error updating income. Please check your input.')
    else:
        form = IncomeForm(instance=income)
    return render(request, 'financial_app/income_form.html', {'form': form, 'title': 'Edit Income'})

@login_required
def delete_income(request, pk):
    """Handles deleting an income entry."""
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        income.delete()
        messages.success(request, 'Income deleted successfully!')
        return redirect('income_list')
    return render(request, 'financial_app/confirm_delete.html', {'object': income, 'title': 'Delete Income'})

# --- Expense Views ---

@login_required
def expense_list(request):
    """Displays a list of all expense entries for the logged-in user."""
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    context = {'expenses': expenses, 'title': 'My Expenses'}
    return render(request, 'financial_app/expense_list.html', context)

@login_required
def add_expense(request):
    """Handles adding a new expense entry."""
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Expense added successfully!')
            return redirect('expense_list')
        else:
            messages.error(request, 'Error adding expense. Please check your input.')
    else:
        form = ExpenseForm()
    return render(request, 'financial_app/expense_form.html', {'form': form, 'title': 'Add Expense'})

@login_required
def edit_expense(request, pk):
    """Handles editing an existing expense entry."""
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully!')
            return redirect('expense_list')
        else:
            messages.error(request, 'Error updating expense. Please check your input.')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'financial_app/expense_form.html', {'form': form, 'title': 'Edit Expense'})

@login_required
def delete_expense(request, pk):
    """Handles deleting an expense entry."""
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted successfully!')
        return redirect('expense_list')
    return render(request, 'financial_app/confirm_delete.html', {'object': expense, 'title': 'Delete Expense'})

# --- Project Views (rest of your views remain the same) ---

@login_required
def project_list(request):
    """Displays a list of all projects for the logged-in user."""
    projects = Project.objects.filter(user=request.user).order_by('is_completed', 'due_date')
    context = {'projects': projects, 'title': 'My Projects'}
    return render(request, 'financial_app/project_list.html', context)

@login_required
def add_project(request):
    """Handles adding a new project."""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            messages.success(request, 'Project added successfully!')
            return redirect('project_list')
        else:
            messages.error(request, 'Error adding project. Please check your input.')
    else:
        form = ProjectForm()
    return render(request, 'financial_app/project_form.html', {'form': form, 'title': 'Add Project'})

@login_required
def edit_project(request, pk):
    """Handles editing an existing project."""
    project = get_object_or_404(Project, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('project_list')
        else:
            messages.error(request, 'Error updating project. Please check your input.')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'financial_app/project_form.html', {'form': form, 'title': 'Edit Project'})

@login_required
def delete_project(request, pk):
    """Handles deleting a project."""
    project = get_object_or_404(Project, pk=pk, user=request.user)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully!')
        return redirect('project_list')
    return render(request, 'financial_app/confirm_delete.html', {'object': project, 'title': 'Delete Project'})

# --- Recommendation and Education Views ---

@login_required
def recommendations_list(request):
    """Displays a list of financial recommendations for the user."""
    recommendations = Recommendation.objects.filter(user=request.user).order_by('-date_created')
    context = {'recommendations': recommendations, 'title': 'Financial Recommendations'}
    return render(request, 'financial_app/recommendations_list.html', context)

@login_required
def education_modules_list(request):
    """Displays a list of financial education modules."""
    education_modules = EducationModule.objects.all().order_by('-date_published')
    context = {'education_modules': education_modules, 'title': 'Financial Education'}
    return render(request, 'financial_app/education_modules_list.html', context)