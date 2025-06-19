# eeuezconsulting_app/eeuezconsulting/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView # Import RedirectView

urlpatterns = [
    # Redirect base URL to login page
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),
    path('admin/', admin.site.urls),
    # Include Django's built-in authentication URLs
    # This provides /accounts/login/, /accounts/logout/, /accounts/password_change/, etc.
    path('accounts/', include('django.contrib.auth.urls')),
    # Include your financial_app URLs
    path('', include('financial_app.urls')),
]

# Serve static files in development (ONLY for DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)