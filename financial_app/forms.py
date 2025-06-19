# eeuezconsulting_app/financial_app/forms.py

from django import forms
from .models import Income, Expense, Project
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

# Custom User Creation Form to include email during registration
class CustomUserCreationForm(UserCreationForm):
    """
    Custom user creation form to extend the default UserCreationForm,
    allowing email to be included in the registration process.
    """
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',) # Add email field

    # Override save method to ensure email is saved
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

# Form for adding/editing Income entries
class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['amount', 'source', 'description']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500', 'placeholder': 'Amount', 'min': '0.01', 'step': '0.01'}),
            'source': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500', 'placeholder': 'e.g., Salary, Freelance'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500', 'rows': 3, 'placeholder': 'Optional description'}),
        }
        labels = {
            'amount': 'Income Amount',
            'source': 'Source of Income',
            'description': 'Description',
        }

# Form for adding/editing Expense entries
class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'category', 'description']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500', 'placeholder': 'Amount', 'min': '0.01', 'step': '0.01'}),
            'category': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500', 'placeholder': 'e.g., Food, Rent, Transport'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500', 'rows': 3, 'placeholder': 'Optional description'}),
        }
        labels = {
            'amount': 'Expense Amount',
            'category': 'Expense Category',
            'description': 'Description',
        }

# Form for adding/editing Project entries
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'target_amount', 'due_date', 'is_completed']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500', 'placeholder': 'Project Name'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500', 'rows': 3, 'placeholder': 'Describe your project (optional)'}),
            'target_amount': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500', 'placeholder': 'Target Amount (optional)', 'min': '0.01', 'step': '0.01'}),
            'due_date': forms.DateInput(attrs={'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500', 'type': 'date'}),
            'is_completed': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-purple-600 rounded'}),
        }
        labels = {
            'name': 'Project Name',
            'description': 'Description',
            'target_amount': 'Target Amount',
            'due_date': 'Due Date',
            'is_completed': 'Completed?',
        }