# Smart Insole Backend

FastAPI backend service for Smart Insole demo application. Provides REST API for sensor data retrieval, signal processing, step detection, pressure heatmap generation, and activity classification.

## Features

- **Sensor Data Management**: Store and retrieve insole sensor data from SQLite database
- **Signal Processing**: Butterworth lowpass filtering and decimation (500Hz → 20Hz)
- **Step Detection**: Peak-based step counting using channels ch2, ch4, ch7
- **Pressure Heatmap**: Generate pressure values for 8 sensor zones (ch0-ch7)
- **Activity Classification**: Mock classifier for walking/sitting/running detection

## Project Structure

```
SmartInsole/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration constants
│   ├── database.py          # SQLite operations
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   ├── routers/
│   │   └── session.py       # API endpoints
│   └── services/
│       ├── signal_processing.py
│       ├── step_detection.py
│       ├── heatmap.py
│       └── classification.py
├── scripts/
│   └── load_csv.py          # CSV to SQLite loader
├── data/
│   └── insole.db            # SQLite database (auto-created)
├── datasets/                 # CSV data files (gitignored)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Installation

### Local Development

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
# Build and run
docker-compose up --build

# Or build manually
docker build -t smartinsole-backend .
docker run -p 8000:8000 -v ./data:/app/data smartinsole-backend
```

## Loading Data

Load CSV data into the database using the provided script:

```bash
# Load new data
python scripts/load_csv.py datasets/new_data_sample.csv

# Clear existing data and load new
python scripts/load_csv.py datasets/new_data_sample.csv --clear
```

### CSV Format

The CSV file must have these columns:
- `device_id`: 1 for left foot, 2 for right foot
- `real_time`: Timestamp string
- `ch0` - `ch7`: Integer sensor values

Optional columns:
- `id`: Record ID (auto-generated if not provided)
- `packet_id`: Packet identifier

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check with database status |
| GET | `/api/session/data` | Raw sensor readings |
| GET | `/api/session/processed` | Filtered/decimated signals |
| GET | `/api/analysis/steps` | Step count and peak detection |
| GET | `/api/analysis/heatmap` | Pressure values per channel |
| GET | `/api/analysis/classification` | Activity classification |

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Configuration

Key configuration parameters in `app/config.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `SAMPLE_RATE` | 500 | Original sensor sample rate (Hz) |
| `TARGET_RATE` | 20 | Target rate after decimation (Hz) |
| `LOWPASS_CUTOFF` | 2.5 | Filter cutoff frequency (Hz) |
| `STEP_CHANNELS` | [2, 4, 7] | Channels for step detection |
| `PEAK_DISTANCE` | 8 | Min samples between peaks |
| `PEAK_HEIGHT` | 100 | Min peak height threshold |
| `BACKEND_PORT` | 8000 | Server port |

## Testing

```bash
# Health check
curl http://localhost:8000/health

# Get step analysis
curl http://localhost:8000/api/analysis/steps

# Get heatmap
curl http://localhost:8000/api/analysis/heatmap
```

## License

MIT
