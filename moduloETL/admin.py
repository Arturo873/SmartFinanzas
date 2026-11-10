from django.contrib import admin
from .models import FinancialUpload, FinancialRatio


@admin.register(FinancialUpload)
class FinancialUploadAdmin(admin.ModelAdmin):
    list_display = ('id', 'period', 'upload_date', 'upload_type', 'status', 'user', 'company')
    list_filter = ('status', 'upload_type', 'company')
    search_fields = ('period', 'source_file')


@admin.register(FinancialRatio)
class FinancialRatioAdmin(admin.ModelAdmin):
    list_display = ('id', 'period', 'calculation_date', 'v1_current_ratio', 'v3_total_leverage', 'is_validated', 'company')
    list_filter = ('is_validated', 'company')
    search_fields = ('period',)
