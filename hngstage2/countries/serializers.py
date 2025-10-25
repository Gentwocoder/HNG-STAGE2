from rest_framework import serializers
from .models import Country


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = [
            'id',
            'name',
            'capital',
            'region',
            'population',
            'currency_code',
            'exchange_rate',
            'estimated_gdp',
            'flag_url',
            'last_refreshed_at'
        ]
        read_only_fields = ['id', 'estimated_gdp', 'last_refreshed_at']

    def validate(self, data):
        """Validate required fields"""
        errors = {}
        
        if not data.get('name'):
            errors['name'] = 'is required'
        
        if not data.get('population'):
            errors['population'] = 'is required'
        
        if not data.get('currency_code'):
            errors['currency_code'] = 'is required'
        
        if errors:
            raise serializers.ValidationError({
                "error": "Validation failed",
                "details": errors
            })
        
        return data
