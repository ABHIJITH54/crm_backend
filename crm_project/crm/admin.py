
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Department, Manager, Staff, Customer


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'profile_picture')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'profile_picture')}),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'department', 'team_name', 'employee_id', 'status', 'joined_date']
    list_filter = ['department', 'status', 'joined_date']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'employee_id', 'team_name']

    @admin.display(description='Full Name')
    def get_full_name(self, obj):
        return obj.user.get_full_name()


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'manager', 'skill', 'employee_id', 'status', 'joined_date']
    list_filter = ['manager', 'status', 'joined_date']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'employee_id', 'skill']

    @admin.display(description='Full Name')
    def get_full_name(self, obj):
        return obj.user.get_full_name()


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'customer_id', 'email', 'phone', 'status', 'gender', 'added_date']
    list_filter = ['status', 'gender', 'added_date']
    search_fields = ['name', 'email', 'phone', 'customer_id']
    readonly_fields = ['customer_id', 'created_at', 'updated_at']
