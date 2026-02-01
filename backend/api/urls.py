from django.urls import path
from .views import RegisterView, LoginView, ProfileView, DashboardSummaryView, PaymentRequestView, MarkPaymentPaidView, AdminMetricsView, AdminUsersView, UnpaidUsersPrintView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('auth/register/', RegisterView.as_view()),
    path('auth/login/', LoginView.as_view()),
    path('auth/refresh/', TokenRefreshView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('dashboard/summary/', DashboardSummaryView.as_view()),
    path('payments/request/', PaymentRequestView.as_view()),
    path('payments/<int:pk>/mark-paid/', MarkPaymentPaidView.as_view()),
    path('admin/metrics/', AdminMetricsView.as_view()),
    path('admin/users/', AdminUsersView.as_view()),
    path('admin/unpaid-users/print/', UnpaidUsersPrintView.as_view()),
]