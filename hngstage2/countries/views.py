import requests
import random
from decimal import Decimal
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.http import FileResponse, JsonResponse
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Country, RefreshMetadata
from .serializers import CountrySerializer
from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path
from decouple import config


COUNTRIES_API_URL = config("COUNTRY_API_URL")
EXCHANGE_RATE_API_URL = config("EXCHANGE_API_URL")


@api_view(['POST'])
def refresh_countries(request):
    """Fetch countries and exchange rates, then cache them in the database"""
    try:
        # Fetch countries data
        try:
            countries_response = requests.get(COUNTRIES_API_URL, timeout=30)
            countries_response.raise_for_status()
            countries_data = countries_response.json()
        except requests.RequestException as e:
            return Response(
                {
                    "error": "External data source unavailable",
                    "details": f"Could not fetch data from restcountries.com: {str(e)}"
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        # Fetch exchange rates
        try:
            rates_response = requests.get(EXCHANGE_RATE_API_URL, timeout=30)
            rates_response.raise_for_status()
            rates_data = rates_response.json()
            exchange_rates = rates_data.get('rates', {})
        except requests.RequestException as e:
            return Response(
                {
                    "error": "External data source unavailable",
                    "details": f"Could not fetch data from open.er-api.com: {str(e)}"
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        # Process and save countries
        countries_count = 0
        for country_data in countries_data:
            name = country_data.get('name')
            capital = country_data.get('capital')
            region = country_data.get('region')
            population = country_data.get('population', 0)
            flag_url = country_data.get('flag')
            currencies = country_data.get('currencies', [])

            # Handle currency
            currency_code = None
            exchange_rate = None
            estimated_gdp = None

            if currencies and len(currencies) > 0:
                # Get first currency code
                currency_code = currencies[0].get('code')
                
                if currency_code:
                    # Get exchange rate
                    exchange_rate = exchange_rates.get(currency_code)
                    
                    # Calculate estimated GDP
                    if exchange_rate and population:
                        random_multiplier = random.uniform(1000, 2000)
                        estimated_gdp = Decimal(population) * Decimal(random_multiplier) / Decimal(exchange_rate)
                    elif population:
                        estimated_gdp = None
            else:
                # No currencies - set GDP to 0
                estimated_gdp = Decimal(0)

            # Update or create country
            country, created = Country.objects.update_or_create(
                name__iexact=name,
                defaults={
                    'name': name,
                    'capital': capital,
                    'region': region,
                    'population': population,
                    'currency_code': currency_code,
                    'exchange_rate': exchange_rate,
                    'estimated_gdp': estimated_gdp,
                    'flag_url': flag_url,
                }
            )
            countries_count += 1

        # Update metadata
        metadata, _ = RefreshMetadata.objects.get_or_create(id=1)
        metadata.total_countries = countries_count
        metadata.save()

        # Generate summary image
        generate_summary_image()

        return Response(
            {
                "message": "Countries data refreshed successfully",
                "total_countries": countries_count,
                "last_refreshed_at": metadata.last_refreshed_at.isoformat()
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {"error": "Internal server error", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def list_countries(request):
    """Get all countries with optional filtering and sorting"""
    try:
        queryset = Country.objects.all()

        # Filter by region
        region = request.query_params.get('region')
        if region:
            queryset = queryset.filter(region__iexact=region)

        # Filter by currency
        currency = request.query_params.get('currency')
        if currency:
            queryset = queryset.filter(currency_code__iexact=currency)

        # Sorting
        sort = request.query_params.get('sort')
        if sort == 'gdp_desc':
            queryset = queryset.order_by('-estimated_gdp')
        elif sort == 'gdp_asc':
            queryset = queryset.order_by('estimated_gdp')
        elif sort == 'population_desc':
            queryset = queryset.order_by('-population')
        elif sort == 'population_asc':
            queryset = queryset.order_by('population')
        elif sort == 'name_asc':
            queryset = queryset.order_by('name')
        elif sort == 'name_desc':
            queryset = queryset.order_by('-name')

        serializer = CountrySerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": "Internal server error", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'DELETE'])
def country_detail(request, name):
    """Get or delete a single country by name"""
    try:
        country = Country.objects.filter(name__iexact=name).first()
        
        if not country:
            return Response(
                {"error": "Country not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if request.method == 'GET':
            serializer = CountrySerializer(country)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif request.method == 'DELETE':
            country_name = country.name
            country.delete()
            
            # Update metadata count
            metadata, _ = RefreshMetadata.objects.get_or_create(id=1)
            metadata.total_countries = Country.objects.count()
            metadata.save()
            
            return Response(
                {"message": f"Country '{country_name}' deleted successfully"},
                status=status.HTTP_200_OK
            )

    except Exception as e:
        return Response(
            {"error": "Internal server error", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_status(request):
    """Get total countries and last refresh timestamp"""
    try:
        metadata, _ = RefreshMetadata.objects.get_or_create(id=1)
        
        # Update count in case it's out of sync
        actual_count = Country.objects.count()
        if metadata.total_countries != actual_count:
            metadata.total_countries = actual_count
            metadata.save()

        return Response(
            {
                "total_countries": metadata.total_countries,
                "last_refreshed_at": metadata.last_refreshed_at.isoformat() if metadata.last_refreshed_at else None
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {"error": "Internal server error", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_summary_image(request):
    """Serve the generated summary image"""
    try:
        # Get the base directory (where manage.py is)
        base_dir = Path(__file__).resolve().parent.parent
        cache_dir = base_dir / 'cache'
        image_path = cache_dir / 'summary.png'

        if not image_path.exists():
            return Response(
                {"error": "Summary image not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return FileResponse(open(image_path, 'rb'), content_type='image/png')

    except Exception as e:
        return Response(
            {"error": "Internal server error", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def generate_summary_image():
    """Generate summary image with countries data"""
    try:
        # Get the base directory
        base_dir = Path(__file__).resolve().parent.parent
        cache_dir = base_dir / 'cache'
        cache_dir.mkdir(exist_ok=True)

        # Get data
        total_countries = Country.objects.count()
        top_countries = Country.objects.filter(
            estimated_gdp__isnull=False
        ).order_by('-estimated_gdp')[:5]
        
        metadata, _ = RefreshMetadata.objects.get_or_create(id=1)
        last_refresh = metadata.last_refreshed_at.strftime('%Y-%m-%d %H:%M:%S UTC') if metadata.last_refreshed_at else 'Never'

        # Create image
        width, height = 800, 600
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)

        # Try to use a font, fallback to default if not available
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
            heading_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
            text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            title_font = ImageFont.load_default()
            heading_font = ImageFont.load_default()
            text_font = ImageFont.load_default()

        y_position = 30

        # Title
        draw.text((30, y_position), "Country Data Summary", fill='black', font=title_font)
        y_position += 60

        # Total countries
        draw.text((30, y_position), f"Total Countries: {total_countries}", fill='black', font=heading_font)
        y_position += 50

        # Top 5 countries by GDP
        draw.text((30, y_position), "Top 5 Countries by Estimated GDP:", fill='black', font=heading_font)
        y_position += 40

        for idx, country in enumerate(top_countries, 1):
            gdp_formatted = f"{country.estimated_gdp:,.2f}" if country.estimated_gdp else "N/A"
            text = f"{idx}. {country.name}: ${gdp_formatted}"
            draw.text((50, y_position), text, fill='blue', font=text_font)
            y_position += 30

        # Last refresh timestamp
        y_position += 30
        draw.text((30, y_position), f"Last Refreshed: {last_refresh}", fill='green', font=text_font)

        # Save image
        image_path = cache_dir / 'summary.png'
        img.save(image_path)

    except Exception as e:
        print(f"Error generating image: {str(e)}")
        # Don't fail the refresh if image generation fails
        pass

