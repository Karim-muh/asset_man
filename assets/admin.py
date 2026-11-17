
from django.contrib import admin

from .models import Department, Employee, Asset, Requisition, Distribution, Disposal, UserProfile


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department_code', 'name', 'location', 'phone', 'email', 'created_at')
    search_fields = ('department_code', 'name', 'location', 'email')
    list_filter = ('location', 'created_at')


admin.site.register(Department, DepartmentAdmin)


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_number', 'first_name', 'last_name', 'email', 'job_title', 'department')
    search_fields = ('employee_number', 'first_name', 'last_name', 'email')
    list_filter = ('department', 'job_title')


admin.site.register(Employee, EmployeeAdmin)


class AssetAdmin(admin.ModelAdmin):
    list_display = ('asset_tag', 'asset_name', 'category', 'serial_number', 'acquisition_date', 'acquisition_cost', 'department', 'status')
    search_fields = ('asset_tag', 'asset_name', 'serial_number')
    list_filter = ('category', 'status', 'department', 'acquisition_date')


admin.site.register(Asset, AssetAdmin)


class RequisitionAdmin(admin.ModelAdmin):
    list_display = ('requisition_number', 'employee', 'asset_category', 'quantity', 'date_requested', 'status')
    search_fields = ('requisition_number', 'employee__first_name', 'employee__last_name')
    list_filter = ('status', 'asset_category', 'date_requested')


admin.site.register(Requisition, RequisitionAdmin)


class DistributionAdmin(admin.ModelAdmin):
    list_display = ('asset', 'employee', 'date_issued', 'expected_return_date', 'actual_return_date', 'condition_on_issue')
    search_fields = ('asset__asset_tag', 'asset__asset_name', 'employee__first_name', 'employee__last_name')
    list_filter = ('date_issued', 'expected_return_date', 'actual_return_date')


admin.site.register(Distribution, DistributionAdmin)


class DisposalAdmin(admin.ModelAdmin):
    list_display = ('asset', 'date_disposed', 'method', 'approved_by', 'disposal_value')
    search_fields = ('asset__asset_tag', 'asset__asset_name', 'approved_by__first_name', 'approved_by__last_name')
    list_filter = ('method', 'date_disposed')


admin.site.register(Disposal, DisposalAdmin)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_approved', 'created_at')
    list_filter = ('role', 'is_approved', 'created_at')
    search_fields = ('user__username', 'user__email')
    list_editable = ('role', 'is_approved')


admin.site.register(UserProfile, UserProfileAdmin)
