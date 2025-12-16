from django.urls import path
from . import views
# from serializers import RegisterView

urlpatterns = [
    path('', views.ReportListCreateView.as_view(), name='report-list-create'),
    path('<int:pk>/', views.ReportDetailView.as_view(), name='report-detail'),
    # path('create/',RegisterView.as_view(), name='register'),
]
