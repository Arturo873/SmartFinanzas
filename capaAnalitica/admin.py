from django.contrib import admin
from .models import RiskPrediction, Recommendation, PDFReport


@admin.register(RiskPrediction)
class RiskPredictionAdmin(admin.ModelAdmin):
    list_display = ('id', 'prediction_date', 'risk_score', 'traffic_light_level', 'model_version', 'executed_by_user', 'company')
    list_filter = ('traffic_light_level', 'model_version', 'company')


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('id', 'prediction', 'source_variable', 'risk_group', 'priority')
    list_filter = ('priority', 'risk_group')


@admin.register(PDFReport)
class PDFReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'prediction', 'generation_date', 'file_path', 'user', 'company')
    list_filter = ('generation_date', 'company')
