from django.contrib import admin
from .models import PaymentMethod, CashRegisterClosure, ClosureMethodDetail, PettyCashWithdrawal, Sale


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'commission_percentage', 'is_active', 'company')
    list_filter = ('is_active', 'company')
    search_fields = ('name',)


@admin.register(CashRegisterClosure)
class CashRegisterClosureAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'status', 'system_total', 'counted_total', 'total_discrepancy', 'closed_by_user', 'company')
    list_filter = ('status', 'date', 'company')
    search_fields = ('date',)


@admin.register(ClosureMethodDetail)
class ClosureMethodDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'closure', 'payment_method', 'system_total', 'counted_total', 'discrepancy')
    list_filter = ('payment_method',)


@admin.register(PettyCashWithdrawal)
class PettyCashWithdrawalAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'amount', 'reason', 'responsible_person', 'user', 'closure', 'company')
    list_filter = ('company', 'date')
    search_fields = ('reason', 'responsible_person')


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'payment_method', 'gross_total', 'charged_total', 'net_income', 'user', 'closure', 'company')
    list_filter = ('payment_method', 'date', 'company')
