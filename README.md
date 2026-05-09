# Trip Kayak — Destination & Hotel Recommender

A data pipeline that recommends the best French travel destinations based on weather forecasts and scrapes top-rated hotels for each city.

---

## Project Overview

This project combines weather data, geographic coordinates and hotel scraping to rank 35 French cities and recommend the best places to visit based on current meteorological conditions.

---

## Pipeline Steps

### 1. Coordinates — `get_coordinates.py`
Fetches latitude and longitude for each city using the **Nominatim / OpenStreetMap API**.

### 2. Weather — `get_weather.py`
Fetches 5-day weather forecasts from the **OpenWeatherMap API** and computes daily averages (09:00–21:00) for each city:
- `rain` — total rainfall (mm)
- `rain_probability` — average probability of rain
- `humidity` — average humidity (%)
- `temp_feels_like` — average felt temperature (°C)
- `wind_speed` — average wind speed (m/s)
- `clouds` — average cloud coverage (%)

### 3. Ranking — `weighted_rank`
Each city is ranked using a **weighted composite score** based on three criteria:

| Criteria | Weight |
|---|---|
| Rain (ascending) | 50% |
| Felt temperature (descending) | 35% |
| Humidity (ascending) | 15% |

→ **Rank 1 = best destination** (least rain, warmest, least humid)

### 4. Hotel Scraping — `booking_spider.py`
Scrapes the top 5 hotels per city from **Booking.com** via **ScraperAPI** (premium rendering). Extracts: hotel name, URL, rating, address and distance from city centre.

### 5. Storage — S3 + Neon PostgreSQL
- Weather data → `trip_Kayak/data/weather_YYYYMMDD_HHMMSS.csv` on **AWS S3**
- Hotels data → `trip_Kayak/data/hotels_YYYYMMDD_HHMMSS.csv` on **AWS S3**
- Both tables loaded into **Neon PostgreSQL**: `trip_kayak_weather` and `trip_kayak_hotels`

### 6. Visualisation — `maps_notebook.py`
Two interactive **Plotly** maps displayed side by side:
- **Map 1** — Top 5 destinations highlighted, with the best-rated hotel per city shown as a star marker
- **Map 2** — All scraped hotels plotted, colour-coded by `weighted_rank` (green = best, red = worst)

---

## Environment Variables (`.env`)

```
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=eu-central-1
S3_BUCKET=your-bucket-name
S3_RAW_FOLDER=trip_Kayak/data/
OPEN_WEATHER_API_KEY=...
SCRAPERAPI_KEY=...
NEON_DB_URL=postgresql://user:password@host/dbname?sslmode=require&channel_binding=require
```

---

## Dependencies

```bash
pip install requests boto3 psycopg2-binary pandas plotly python-dotenv lxml scrapy scrapy-playwright
playwright install chromium
```

---

## Database Schema

**`trip_kayak_weather`** — one row per city  
**`trip_kayak_hotels`** — one row per hotel, joined to weather table on `city`

```sql
SELECT w.city, w.weighted_rank, w.temp_feels_like, h.nom, h.note_score, h.distance_km
FROM trip_kayak_weather w
JOIN trip_kayak_hotels h ON w.city = h.city
ORDER BY w.weighted_rank, h.note_score DESC;
```
