
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView, register_admin, dashboard_stats,
    departments_list_create, department_detail,
    managers_list_create, manager_detail,
    staff_list_create, staff_detail,
    customers_list_create, customer_detail,
    managers_dropdown, departments_dropdown
)

urlpatterns = [
    # Auth
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', register_admin, name='register_admin'),

    # Dashboard
    path('dashboard/stats/', dashboard_stats, name='dashboard_stats'),

    # Departments
    path('departments/', departments_list_create, name='departments_list_create'),
    path('departments/<int:pk>/', department_detail, name='department_detail'),

    # Managers
    path('managers/', managers_list_create, name='managers_list_create'),
    path('managers/<int:pk>/', manager_detail, name='manager_detail'),

    # Staff
    path('staff/', staff_list_create, name='staff_list_create'),
    path('staff/<int:pk>/', staff_detail, name='staff_detail'),

    # Customers
    path('customers/', customers_list_create, name='customers_list_create'),
    path('customers/<int:pk>/', customer_detail, name='customer_detail'),

    # Dropdowns
    path('managers/list/', managers_dropdown, name='managers_list'),
    path('departments/list/', departments_dropdown, name='departments_list'),
]
