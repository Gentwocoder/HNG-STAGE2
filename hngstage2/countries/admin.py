from django.contrib import admin
from .models import Country, RefreshMetadata


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'capital', 'region', 'population', 'currency_code', 'exchange_rate', 'estimated_gdp', 'last_refreshed_at']
    list_filter = ['region', 'currency_code']
    search_fields = ['name', 'capital', 'region']
    ordering = ['name']


@admin.register(RefreshMetadata)
class RefreshMetadataAdmin(admin.ModelAdmin):
    list_display = ['id', 'total_countries', 'last_refreshed_at']

