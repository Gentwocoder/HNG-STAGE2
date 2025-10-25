from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)
    capital = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    population = models.BigIntegerField()
    currency_code = models.CharField(max_length=10, blank=True, null=True)
    exchange_rate = models.DecimalField(max_digits=20, decimal_places=6, blank=True, null=True)
    estimated_gdp = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)
    flag_url = models.URLField(max_length=500, blank=True, null=True)
    last_refreshed_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Countries"
        ordering = ['name']

    def __str__(self):
        return self.name


class RefreshMetadata(models.Model):
    last_refreshed_at = models.DateTimeField(auto_now=True)
    total_countries = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Refresh Metadata"
