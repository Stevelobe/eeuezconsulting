# eeuezconsulting_app/financial_app/admin.py

from django.contrib import admin
from .models import UserProfile, Income, Expense, Recommendation, Project, EducationModule
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# Register your models here.

# Inline for UserProfile to integrate with User admin
# This allows UserProfile fields to be edited directly from the User admin page.
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False # Prevent accidental deletion of the profile when deleting a user
    verbose_name_plural = 'profile' # Display name in admin
    # Define fields to be displayed in the inline form
    fields = ('financial_goal', 'risk_tolerance', 'date_of_birth', 'occupation')


# Define a new User admin that includes the UserProfile inline
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_financial_goal')

    # Add a custom method to display financial goal in the User list
    def get_financial_goal(self, obj):
        # Ensure the profile exists before trying to access it
        return obj.profile.financial_goal if hasattr(obj, 'profile') else 'N/A'
    get_financial_goal.short_description = 'Financial Goal' # Column header in admin

# Re-register UserAdmin to use our custom UserAdmin
# First unregister the default User admin
admin.site.unregister(User)
# Then register our custom User admin
admin.site.register(User, UserAdmin)

# Register other models directly with custom Admin classes for better management
@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'source', 'date')
    list_filter = ('source', 'date', 'user')
    search_fields = ('source', 'description')
    date_hierarchy = 'date' # Adds a navigation bar by date

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'category', 'date')
    list_filter = ('category', 'date', 'user')
    search_fields = ('category', 'description')
    date_hierarchy = 'date'

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'date_created')
    list_filter = ('is_read', 'date_created', 'user')
    search_fields = ('title', 'content')
    date_hierarchy = 'date_created'

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'target_amount', 'current_amount', 'due_date', 'is_completed')
    list_filter = ('is_completed', 'due_date', 'user')
    search_fields = ('name', 'description')
    date_hierarchy = 'start_date'

@admin.register(EducationModule)
class EducationModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'ehblo_link', 'date_published')
    list_filter = ('date_published',)
    search_fields = ('title', 'description', 'content')