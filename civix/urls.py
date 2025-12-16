from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('apps.users.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/comments/', include('apps.comments.urls')),
    path('api/notifications/', include('apps.notification.urls')),
    path('api/assignements/', include('apps.assignements.urls')),
    path('api/categories/', include('apps.category.urls')),
]
