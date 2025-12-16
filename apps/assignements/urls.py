from django.urls import path
from . import views

urlpatterns = [
    path('', views.AssignmentListCreateView.as_view(), name='assignment-list-create'),
    path('<int:pk>/', views.AssignmentDetailView.as_view(), name='assignment-detail'),
]
