from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationListCreateView.as_view(), name='notification-list-create'),
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
]
