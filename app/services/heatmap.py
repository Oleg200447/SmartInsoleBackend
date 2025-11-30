"""Heatmap generation service for pressure visualization"""

from typing import Dict, List, Any
import numpy as np

from app.config import (
    PRESSURE_PERCENTILE_LOW,
    PRESSURE_PERCENTILE_HIGH,
    PRESSURE_MIN,
    PRESSURE_MAX,
    NUM_CHANNELS,
)


def calculate_pressure(
    signal: np.ndarray,
    percentile_low: float = PRESSURE_PERCENTILE_LOW,
    percentile_high: float = PRESSURE_PERCENTILE_HIGH
) -> float:
    """
    Calculate pressure value from signal using top percentile mean.
    
    Algorithm:
    1. Find values in the specified percentile range (90-100%)
    2. Calculate mean of those values
    3. Subtract overall mean to get relative pressure
    
    Args:
        signal: Input signal array
        percentile_low: Lower percentile bound
        percentile_high: Upper percentile bound
        
    Returns:
        Pressure value (can be negative or positive)
    """
    if len(signal) == 0:
        return 0.0
    
    # Calculate percentile thresholds
    low_threshold = np.percentile(signal, percentile_low)
    high_threshold = np.percentile(signal, percentile_high)
    
    # Get values in percentile range
    mask = (signal >= low_threshold) & (signal <= high_threshold)
    top_values = signal[mask]
    
    if len(top_values) == 0:
        return float(np.mean(signal))
    
    # Calculate mean of top percentile values
    top_mean = float(np.mean(top_values))
    
    # Subtract overall mean to get relative pressure
    overall_mean = float(np.mean(signal))
    
    return top_mean - overall_mean


def normalize_pressure(
    value: float, 
    min_val: float = PRESSURE_MIN, 
    max_val: float = PRESSURE_MAX,
    data_min: float = 0.0,
    data_max: float = 1000.0
) -> float:
    """
    Scale pressure value to target range.
    
    Args:
        value: Input pressure value
        min_val: Target minimum (default: 0)
        max_val: Target maximum (default: 999)
        data_min: Expected data minimum
        data_max: Expected data maximum
        
    Returns:
        Normalized pressure value in [min_val, max_val]
    """
    if data_max == data_min:
        return (min_val + max_val) / 2
    
    # Normalize to [0, 1]
    normalized = (value - data_min) / (data_max - data_min)
    
    # Clip to [0, 1]
    normalized = max(0.0, min(1.0, normalized))
    
    # Scale to target range
    scaled = min_val + normalized * (max_val - min_val)
    
    return scaled


def generate_heatmap(
    channels: Dict[str, np.ndarray],
    normalize: bool = True
) -> Dict[str, float]:
    """
    Generate pressure heatmap values for all channels.
    
    Args:
        channels: Dictionary of processed channel arrays
        normalize: Whether to normalize to 0-999 range
        
    Returns:
        Dictionary mapping channel names to pressure values
    """
    pressures = {}
    raw_pressures = []
    
    # Calculate raw pressure for each channel
    for i in range(NUM_CHANNELS):
        channel_name = f"ch{i}"
        if channel_name in channels and len(channels[channel_name]) > 0:
            pressure = calculate_pressure(channels[channel_name])
            pressures[channel_name] = pressure
            raw_pressures.append(pressure)
        else:
            pressures[channel_name] = 0.0
    
    # Normalize if requested
    if normalize and raw_pressures:
        data_min = min(raw_pressures)
        data_max = max(raw_pressures)
        
        # Add some padding to avoid 0 and max for all
        if data_max == data_min:
            data_min = data_min - 1
            data_max = data_max + 1
        
        for channel_name in pressures:
            pressures[channel_name] = normalize_pressure(
                pressures[channel_name],
                min_val=PRESSURE_MIN,
                max_val=PRESSURE_MAX,
                data_min=data_min,
                data_max=data_max
            )
    
    return pressures


def calculate_pressure_from_readings(
    readings: List[Dict[str, Any]]
) -> Dict[str, float]:
    """
    Calculate pressure values directly from raw readings.
    
    This is a convenience function that combines channel extraction
    and heatmap generation.
    
    Args:
        readings: List of sensor reading dictionaries
        
    Returns:
        Dictionary mapping channel names to normalized pressure values
    """
    if not readings:
        return {f"ch{i}": 0.0 for i in range(NUM_CHANNELS)}
    
    # Extract channels
    channels = {}
    for i in range(NUM_CHANNELS):
        channel_name = f"ch{i}"
        channels[channel_name] = np.array([r[channel_name] for r in readings], dtype=float)
    
    return generate_heatmap(channels, normalize=True)


def get_pressure_color(pressure: float, max_pressure: float = PRESSURE_MAX) -> str:
    """
    Get color for pressure value (for visualization).
    
    Color scale: green (low) -> yellow -> red (high)
    
    Args:
        pressure: Pressure value
        max_pressure: Maximum pressure for normalization
        
    Returns:
        RGB color string
    """
    # Normalize to [0, 1]
    ratio = pressure / max_pressure if max_pressure > 0 else 0
    ratio = max(0.0, min(1.0, ratio))
    
    # Color mapping
    pressure_colors = [
        "rgb(0,255,0)",      # 0-10%
        "rgb(51,255,0)",     # 10-20%
        "rgb(102,255,0)",    # 20-30%
        "rgb(153,255,0)",    # 30-40%
        "rgb(204,255,0)",    # 40-50%
        "rgb(255,255,0)",    # 50-60%
        "rgb(255,204,0)",    # 60-70%
        "rgb(255,153,0)",    # 70-80%
        "rgb(255,102,0)",    # 80-90%
        "rgb(255,0,0)",      # 90-100%
    ]
    
    idx = min(int(ratio * 10), 9)
    return pressure_colors[idx]
