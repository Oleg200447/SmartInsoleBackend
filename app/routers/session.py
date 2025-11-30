"""API endpoints for session data and analysis"""

from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException

from app.database import get_session_data, get_data_count, check_database_exists
from app.models.schemas import (
    SensorReading,
    SessionData,
    ProcessedSignal,
    ProcessedData,
    StepAnalysis,
    StepsResponse,
    HeatmapData,
    HeatmapResponse,
    ClassificationResult,
    HealthResponse,
)
from app.services.signal_processing import process_channels, generate_timestamps
from app.services.step_detection import detect_steps
from app.services.heatmap import generate_heatmap
from app.services.classification import classify_activity
from app.config import TARGET_RATE

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns service status, database connection status, and data counts.
    """
    db_exists = check_database_exists()
    
    try:
        if db_exists:
            data_count = get_data_count()
            db_status = "connected"
        else:
            data_count = {"left": 0, "right": 0, "total": 0}
            db_status = "no_database"
    except Exception as e:
        data_count = None
        db_status = f"error: {str(e)}"
    
    return HealthResponse(
        status="healthy",
        database=db_status,
        timestamp=datetime.utcnow().isoformat() + "Z",
        data_count=data_count
    )


@router.get("/api/session/data", response_model=SessionData, tags=["Session"])
async def get_raw_session_data():
    """
    Get raw session data for both feet.
    
    Returns sensor readings separated by device_id (left/right foot).
    """
    try:
        left_data, right_data = get_session_data()
        
        left_readings = [SensorReading(**r) for r in left_data]
        right_readings = [SensorReading(**r) for r in right_data]
        
        return SessionData(
            left_foot=left_readings,
            right_foot=right_readings
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/api/session/processed", response_model=ProcessedData, tags=["Session"])
async def get_processed_data():
    """
    Get processed (filtered and decimated) session data.
    
    Processing pipeline:
    1. Lowpass filter (2.5Hz cutoff)
    2. Decimation from 500Hz to 20Hz
    """
    try:
        left_data, right_data = get_session_data()
        
        # Process left foot
        left_channels = process_channels(left_data)
        left_num_samples = len(next(iter(left_channels.values()))) if left_channels else 0
        left_timestamps = generate_timestamps(left_num_samples, TARGET_RATE).tolist()
        
        # Process right foot  
        right_channels = process_channels(right_data)
        right_num_samples = len(next(iter(right_channels.values()))) if right_channels else 0
        right_timestamps = generate_timestamps(right_num_samples, TARGET_RATE).tolist()
        
        # Convert numpy arrays to lists for JSON serialization
        left_channels_list = {k: v.tolist() for k, v in left_channels.items()}
        right_channels_list = {k: v.tolist() for k, v in right_channels.items()}
        
        return ProcessedData(
            left_foot=ProcessedSignal(
                timestamps=left_timestamps,
                channels=left_channels_list
            ),
            right_foot=ProcessedSignal(
                timestamps=right_timestamps,
                channels=right_channels_list
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@router.get("/api/analysis/steps", response_model=StepsResponse, tags=["Analysis"])
async def get_steps_analysis():
    """
    Get step detection analysis for both feet.
    
    Uses channels ch2, ch4, ch7 averaged together, then finds peaks
    with minimum distance=8 and height=100.
    """
    try:
        left_data, right_data = get_session_data()
        
        # Process and detect steps for left foot
        left_channels = process_channels(left_data)
        left_step_count, left_peaks, left_signal = detect_steps(left_channels)
        left_num_samples = len(left_signal) if len(left_signal) > 0 else 0
        left_timestamps = generate_timestamps(left_num_samples, TARGET_RATE).tolist()
        
        # Process and detect steps for right foot
        right_channels = process_channels(right_data)
        right_step_count, right_peaks, right_signal = detect_steps(right_channels)
        right_num_samples = len(right_signal) if len(right_signal) > 0 else 0
        right_timestamps = generate_timestamps(right_num_samples, TARGET_RATE).tolist()
        
        return StepsResponse(
            left_foot=StepAnalysis(
                step_count=left_step_count,
                peak_indices=left_peaks,
                signal_data=left_signal.tolist() if len(left_signal) > 0 else [],
                timestamps=left_timestamps
            ),
            right_foot=StepAnalysis(
                step_count=right_step_count,
                peak_indices=right_peaks,
                signal_data=right_signal.tolist() if len(right_signal) > 0 else [],
                timestamps=right_timestamps
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Step analysis error: {str(e)}")


@router.get("/api/analysis/heatmap", response_model=HeatmapResponse, tags=["Analysis"])
async def get_heatmap():
    """
    Get pressure heatmap data for both feet.
    
    Calculates pressure values for each channel (ch0-ch7) using
    90-100 percentile mean, normalized to 0-999 range.
    """
    try:
        left_data, right_data = get_session_data()
        
        # Process channels
        left_channels = process_channels(left_data)
        right_channels = process_channels(right_data)
        
        # Generate heatmaps
        left_pressures = generate_heatmap(left_channels)
        right_pressures = generate_heatmap(right_channels)
        
        return HeatmapResponse(
            left_foot=HeatmapData(pressures=left_pressures),
            right_foot=HeatmapData(pressures=right_pressures)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Heatmap error: {str(e)}")


@router.get("/api/analysis/classification", response_model=ClassificationResult, tags=["Analysis"])
async def get_classification():
    """
    Get activity classification result.
    
    Currently returns mock/random classification.
    Possible activities: walking, sitting, running.
    """
    try:
        activity, confidence = classify_activity()
        
        return ClassificationResult(
            activity=activity,
            confidence=round(confidence, 2)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")
