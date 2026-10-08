from django.contrib import admin
from .models import Profession, ProfessionTypeWeights


class ProfessionTypeWeightsInline(admin.StackedInline):
    model = ProfessionTypeWeights
    extra = 0


@admin.register(Profession)
class ProfessionAdmin(admin.ModelAdmin):
    list_display = ['profession_id', 'name', 'category', 'avg_salary', 'demand_level']
    list_filter = ['category', 'demand_level']
    search_fields = ['name', 'category']
    inlines = [ProfessionTypeWeightsInline]
