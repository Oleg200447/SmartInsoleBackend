"""Pydantic schemas for API request/response models"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SensorReading(BaseModel):
    """Single sensor data point from insole"""
    id: Optional[int] = None
    device_id: int = Field(..., description="1=left foot, 2=right foot")
    packet_id: Optional[int] = None
    real_time: str = Field(..., description="Timestamp of the reading")
    ch0: int = Field(..., description="Channel 0 sensor value")
    ch1: int = Field(..., description="Channel 1 sensor value")
    ch2: int = Field(..., description="Channel 2 sensor value")
    ch3: int = Field(..., description="Channel 3 sensor value")
    ch4: int = Field(..., description="Channel 4 sensor value")
    ch5: int = Field(..., description="Channel 5 sensor value")
    ch6: int = Field(..., description="Channel 6 sensor value")
    ch7: int = Field(..., description="Channel 7 sensor value")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "device_id": 1,
                "packet_id": 100,
                "real_time": "2024-01-15 10:30:00.123",
                "ch0": 512, "ch1": 480, "ch2": 520, "ch3": 490,
                "ch4": 510, "ch5": 530, "ch6": 500, "ch7": 515
            }
        }


class SessionData(BaseModel):
    """Raw session data response for both feet"""
    left_foot: List[SensorReading] = Field(default_factory=list, description="Left foot sensor data (device_id=1)")
    right_foot: List[SensorReading] = Field(default_factory=list, description="Right foot sensor data (device_id=2)")


class ProcessedSignal(BaseModel):
    """Processed signal data after filtering and decimation"""
    timestamps: List[float] = Field(default_factory=list, description="Time points after decimation")
    channels: Dict[str, List[float]] = Field(default_factory=dict, description="Processed values for ch0-ch7")


class ProcessedData(BaseModel):
    """Processed data for both feet"""
    left_foot: ProcessedSignal = Field(default_factory=ProcessedSignal)
    right_foot: ProcessedSignal = Field(default_factory=ProcessedSignal)


class StepAnalysis(BaseModel):
    """Step detection results for a single foot"""
    step_count: int = Field(0, description="Number of steps detected")
    peak_indices: List[int] = Field(default_factory=list, description="Indices of detected peaks")
    signal_data: List[float] = Field(default_factory=list, description="Combined signal used for detection")
    timestamps: List[float] = Field(default_factory=list, description="Time points for the signal")


class StepsResponse(BaseModel):
    """Step analysis response for both feet"""
    left_foot: StepAnalysis = Field(default_factory=StepAnalysis)
    right_foot: StepAnalysis = Field(default_factory=StepAnalysis)


class HeatmapData(BaseModel):
    """Pressure heatmap data for a single foot"""
    pressures: Dict[str, float] = Field(
        default_factory=dict, 
        description="Pressure values (0-999) for each channel (ch0-ch7)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "pressures": {
                    "ch0": 450.5, "ch1": 320.0, "ch2": 580.2, "ch3": 410.8,
                    "ch4": 390.1, "ch5": 520.5, "ch6": 480.3, "ch7": 550.9
                }
            }
        }


class HeatmapResponse(BaseModel):
    """Heatmap response for both feet"""
    left_foot: HeatmapData = Field(default_factory=HeatmapData)
    right_foot: HeatmapData = Field(default_factory=HeatmapData)


class ClassificationResult(BaseModel):
    """Activity classification result"""
    activity: str = Field(..., description="Classified activity: walking, sitting, or running")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence score")

    class Config:
        json_schema_extra = {
            "example": {
                "activity": "walking",
                "confidence": 0.85
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    database: str = Field(..., description="Database connection status")
    timestamp: str = Field(..., description="Current server timestamp")
    data_count: Optional[Dict[str, int]] = Field(None, description="Record counts in database")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "database": "connected",
                "timestamp": "2024-01-15T10:30:00Z",
                "data_count": {"left": 1000, "right": 1000, "total": 2000}
            }
        }
