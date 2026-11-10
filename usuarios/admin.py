from django.contrib import admin
from .models import Role, Company, User


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'business_name', 'tax_id', 'business_sector', 'debit_commission_pct', 'credit_commission_pct')
    search_fields = ('business_name', 'tax_id')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'role', 'company', 'is_active', 'created_at')
    list_filter = ('is_active', 'role')
    search_fields = ('username', 'email')
