#!/usr/bin/env python
"""
Test script for Country Currency & Exchange API
Run this after starting the development server with: python manage.py runserver
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_response(title, response):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_api():
    """Test all API endpoints"""
    
    # 1. Test status endpoint (before refresh)
    print("\n1. Testing GET /status (before refresh)")
    response = requests.get(f"{BASE_URL}/status")
    print_response("GET /status", response)
    
    # 2. Test refresh endpoint
    print("\n2. Testing POST /countries/refresh")
    print("Note: This may take 30-60 seconds...")
    response = requests.post(f"{BASE_URL}/countries/refresh")
    print_response("POST /countries/refresh", response)
    
    # Wait a moment for processing
    time.sleep(2)
    
    # 3. Test get all countries
    print("\n3. Testing GET /countries")
    response = requests.get(f"{BASE_URL}/countries")
    print_response("GET /countries (first 3)", response)
    if response.status_code == 200:
        data = response.json()
        print(f"Total countries returned: {len(data)}")
        if len(data) > 0:
            print(f"First country: {data[0]['name']}")
    
    # 4. Test filter by region
    print("\n4. Testing GET /countries?region=Africa")
    response = requests.get(f"{BASE_URL}/countries?region=Africa")
    print_response("GET /countries?region=Africa", response)
    if response.status_code == 200:
        data = response.json()
        print(f"African countries: {len(data)}")
    
    # 5. Test filter by currency
    print("\n5. Testing GET /countries?currency=USD")
    response = requests.get(f"{BASE_URL}/countries?currency=USD")
    print_response("GET /countries?currency=USD", response)
    if response.status_code == 200:
        data = response.json()
        print(f"Countries using USD: {len(data)}")
    
    # 6. Test sort by GDP
    print("\n6. Testing GET /countries?sort=gdp_desc")
    response = requests.get(f"{BASE_URL}/countries?sort=gdp_desc")
    print_response("GET /countries?sort=gdp_desc (top 5)", response)
    if response.status_code == 200:
        data = response.json()
        print("\nTop 5 countries by GDP:")
        for i, country in enumerate(data[:5], 1):
            gdp = country.get('estimated_gdp', 'N/A')
            print(f"  {i}. {country['name']}: ${gdp}")
    
    # 7. Test get single country
    print("\n7. Testing GET /countries/Nigeria")
    response = requests.get(f"{BASE_URL}/countries/Nigeria")
    print_response("GET /countries/Nigeria", response)
    
    # 8. Test status endpoint (after refresh)
    print("\n8. Testing GET /status (after refresh)")
    response = requests.get(f"{BASE_URL}/status")
    print_response("GET /status", response)
    
    # 9. Test summary image
    print("\n9. Testing GET /countries/image")
    response = requests.get(f"{BASE_URL}/countries/image")
    if response.status_code == 200:
        print("✓ Summary image endpoint is working")
        print(f"  Content-Type: {response.headers.get('Content-Type')}")
        print(f"  Image size: {len(response.content)} bytes")
        # Optionally save the image
        with open('test_summary.png', 'wb') as f:
            f.write(response.content)
        print("  Image saved to: test_summary.png")
    else:
        print_response("GET /countries/image", response)
    
    # 10. Test delete country (optional - uncomment to test)
    # print("\n10. Testing DELETE /countries/TestCountry")
    # response = requests.delete(f"{BASE_URL}/countries/TestCountry")
    # print_response("DELETE /countries/TestCountry", response)
    
    # 11. Test 404 error
    print("\n11. Testing GET /countries/NonExistentCountry (should return 404)")
    response = requests.get(f"{BASE_URL}/countries/NonExistentCountry12345")
    print_response("GET /countries/NonExistentCountry", response)
    
    print("\n" + "="*60)
    print("Testing complete!")
    print("="*60)

if __name__ == "__main__":
    print("Country Currency & Exchange API - Test Script")
    print("="*60)
    print("Make sure the server is running: python manage.py runserver")
    print("="*60)
    
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server")
        print("Please make sure the Django server is running:")
        print("  python manage.py runserver")
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
