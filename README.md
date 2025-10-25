# Country Currency & Exchange Rate API

A RESTful API built with Django and Django REST Framework that fetches country data from external APIs, stores it in a database, and provides CRUD operations with filtering and sorting capabilities.

## Features

- Fetch country data from REST Countries API
- Fetch exchange rates from Open Exchange Rates API
- Calculate estimated GDP based on population and exchange rates
- Store and cache data in database (SQLite or MySQL)
- Full CRUD operations on country data
- Filter countries by region or currency
- Sort countries by various fields
- Generate summary images with top countries
- Comprehensive error handling

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/countries/refresh` | Fetch and cache all countries and exchange rates |
| GET | `/countries` | Get all countries (supports filtering and sorting) |
| GET | `/countries/:name` | Get a single country by name |
| DELETE | `/countries/:name` | Delete a country record |
| GET | `/status` | Get total countries and last refresh timestamp |
| GET | `/countries/image` | Serve the summary image |

### Query Parameters

**GET /countries**
- `?region=Africa` - Filter by region
- `?currency=NGN` - Filter by currency code
- `?sort=gdp_desc` - Sort by estimated GDP (descending)
- `?sort=gdp_asc` - Sort by estimated GDP (ascending)
- `?sort=population_desc` - Sort by population (descending)
- `?sort=population_asc` - Sort by population (ascending)
- `?sort=name_asc` - Sort by name (A-Z)
- `?sort=name_desc` - Sort by name (Z-A)

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip
- MySQL (optional, SQLite is used by default)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd hngstage2
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration

Create a `.env` file in the project root:

```bash
nano .env
```

Edit `.env` and configure your settings:

**For SQLite (Default):**
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

**For MySQL:**
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=django.db.backends.mysql
DB_NAME=countries_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306
```

### Step 5: Update Settings (Optional - for MySQL)

If using MySQL, update `hngstage2/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DB_NAME', default=BASE_DIR / 'db.sqlite3'),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default=''),
    }
}
```

### Step 6: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 7: Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### Step 8: Run the Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## Usage Examples

### 1. Refresh Country Data

```bash
curl -X POST http://localhost:8000/countries/refresh
```

**Response:**
```json
{
  "message": "Countries data refreshed successfully",
  "total_countries": 250,
  "last_refreshed_at": "2025-10-25T18:00:00Z"
}
```

### 2. Get All Countries

```bash
curl http://localhost:8000/countries
```

### 3. Filter Countries by Region

```bash
curl http://localhost:8000/countries?region=Africa
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Nigeria",
    "capital": "Abuja",
    "region": "Africa",
    "population": 206139589,
    "currency_code": "NGN",
    "exchange_rate": "1600.230000",
    "estimated_gdp": "25767448125.20",
    "flag_url": "https://flagcdn.com/ng.svg",
    "last_refreshed_at": "2025-10-25T18:00:00Z"
  }
]
```

### 4. Filter by Currency

```bash
curl http://localhost:8000/countries?currency=USD
```

### 5. Sort by GDP

```bash
curl http://localhost:8000/countries?sort=gdp_desc
```

### 6. Get Single Country

```bash
curl http://localhost:8000/countries/Nigeria
```

### 7. Delete a Country

```bash
curl -X DELETE http://localhost:8000/countries/Nigeria
```

**Response:**
```json
{
  "message": "Country 'Nigeria' deleted successfully"
}
```

### 8. Get Status

```bash
curl http://localhost:8000/status
```

**Response:**
```json
{
  "total_countries": 250,
  "last_refreshed_at": "2025-10-25T18:00:00Z"
}
```

### 9. Get Summary Image

```bash
curl http://localhost:8000/countries/image --output summary.png
```

Or open in browser: `http://localhost:8000/countries/image`

## Data Model

### Country Model

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Auto-generated primary key |
| name | String | Country name (unique, required) |
| capital | String | Capital city (optional) |
| region | String | Geographic region (optional) |
| population | BigInteger | Population count (required) |
| currency_code | String | Currency code (optional) |
| exchange_rate | Decimal | Exchange rate vs USD (optional) |
| estimated_gdp | Decimal | Calculated GDP estimate (optional) |
| flag_url | URL | Flag image URL (optional) |
| last_refreshed_at | DateTime | Last update timestamp (auto) |

## Business Logic

### Refresh Process

1. Fetch countries from REST Countries API
2. Fetch exchange rates from Open Exchange Rates API
3. For each country:
   - Extract first currency code (if available)
   - Get exchange rate for that currency
   - Calculate estimated GDP: `population × random(1000-2000) ÷ exchange_rate`
   - Update existing country or create new one (case-insensitive name match)
4. Update global refresh timestamp
5. Generate summary image

### Currency Handling

- **Multiple currencies**: Uses first currency only
- **No currencies**: Sets currency_code=null, exchange_rate=null, estimated_gdp=0
- **Currency not in exchange rates**: Sets exchange_rate=null, estimated_gdp=null

### Error Handling

The API returns consistent JSON error responses:

- **404 Not Found**: `{"error": "Country not found"}`
- **400 Bad Request**: `{"error": "Validation failed", "details": {...}}`
- **500 Internal Server Error**: `{"error": "Internal server error"}`
- **503 Service Unavailable**: `{"error": "External data source unavailable", "details": "..."}`

## Testing

### Manual Testing

Use curl, Postman, or any HTTP client to test the endpoints.

### Running Tests (if implemented)

```bash
python manage.py test countries
```

## Project Structure

```
hngstage2/
├── cache/                      # Generated images
│   └── summary.png
├── countries/                  # Main app
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py              # Country and RefreshMetadata models
│   ├── serializers.py         # DRF serializers
│   ├── views.py               # API views
│   ├── urls.py                # App URLs
│   └── tests.py
├── hngstage2/                 # Project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

## External APIs Used

1. **REST Countries API**: https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies
   - Provides country information

2. **Open Exchange Rates API**: https://open.er-api.com/v6/latest/USD
   - Provides currency exchange rates

## Notes

- The API uses SQLite by default for easy setup
- For production, consider using PostgreSQL or MySQL
- The estimated GDP calculation uses a random multiplier (1000-2000) for demonstration purposes
- Exchange rates are fetched in real-time during refresh
- Summary images are generated using Pillow (PIL)

