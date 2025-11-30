"""Step detection service using peak analysis"""

from typing import Dict, List, Tuple
import numpy as np
from scipy.signal import find_peaks

from app.config import (
    STEP_CHANNELS,
    PEAK_DISTANCE,
    PEAK_HEIGHT,
    TARGET_RATE,
)
from app.services.signal_processing import prep_signal


def combine_step_channels(
    channels: Dict[str, np.ndarray], 
    indices: List[int] = STEP_CHANNELS
) -> np.ndarray:
    """
    Average specified channels for step detection.
    
    Args:
        channels: Dictionary of processed channel arrays
        indices: List of channel indices to combine (default: [2, 4, 7])
        
    Returns:
        Combined signal array (average of specified channels)
    """
    if not channels:
        return np.array([])
    
    # Get signals for specified channels
    signals = []
    for idx in indices:
        channel_name = f"ch{idx}"
        if channel_name in channels and len(channels[channel_name]) > 0:
            signals.append(channels[channel_name])
    
    if not signals:
        return np.array([])
    
    # Ensure all signals have the same length
    min_length = min(len(s) for s in signals)
    signals = [s[:min_length] for s in signals]
    
    # Stack and compute mean
    stacked = np.vstack(signals)
    return np.mean(stacked, axis=0)


def detect_steps(
    channels: Dict[str, np.ndarray],
    step_channels: List[int] = STEP_CHANNELS,
    distance: int = PEAK_DISTANCE,
    height: float = PEAK_HEIGHT
) -> Tuple[int, List[int], np.ndarray]:
    """
    Detect steps by finding peaks in combined signal.
    
    Algorithm:
    1. Combine specified channels (ch2, ch4, ch7)
    2. Prepare signal (remove baseline, normalize)
    3. Find peaks with minimum distance and height
    
    Args:
        channels: Dictionary of processed channel arrays
        step_channels: Channel indices to use for detection
        distance: Minimum samples between peaks
        height: Minimum peak height
        
    Returns:
        Tuple of (step_count, peak_indices, combined_signal)
    """
    if not channels:
        return 0, [], np.array([])
    
    # Combine channels
    combined = combine_step_channels(channels, step_channels)
    
    if len(combined) == 0:
        return 0, [], np.array([])
    
    # Prepare each channel individually and then combine
    prepped_signals = []
    for idx in step_channels:
        channel_name = f"ch{idx}"
        if channel_name in channels and len(channels[channel_name]) > 0:
            prepped = prep_signal(channels[channel_name])
            prepped_signals.append(prepped)
    
    if not prepped_signals:
        return 0, [], combined
    
    # Ensure all signals have the same length
    min_length = min(len(s) for s in prepped_signals)
    prepped_signals = [s[:min_length] for s in prepped_signals]
    
    # Average the prepared signals
    prepped_combined = np.mean(np.vstack(prepped_signals), axis=0)
    
    # Find peaks
    peaks, properties = find_peaks(prepped_combined, distance=distance, height=height)
    
    step_count = len(peaks)
    peak_indices = peaks.tolist()
    
    return step_count, peak_indices, prepped_combined


def generate_step_timestamps(
    peak_indices: List[int], 
    fs: float = TARGET_RATE
) -> List[float]:
    """
    Convert peak indices to timestamps.
    
    Args:
        peak_indices: List of sample indices where peaks occur
        fs: Sample rate
        
    Returns:
        List of timestamps in seconds
    """
    return [idx / fs for idx in peak_indices]


def calculate_step_metrics(
    peak_indices: List[int],
    fs: float = TARGET_RATE
) -> Dict[str, float]:
    """
    Calculate step-related metrics.
    
    Args:
        peak_indices: List of peak indices
        fs: Sample rate
        
    Returns:
        Dictionary with metrics (cadence, avg_step_time, etc.)
    """
    if len(peak_indices) < 2:
        return {
            "cadence_steps_per_min": 0.0,
            "avg_step_time_sec": 0.0,
            "step_time_std_sec": 0.0,
        }
    
    # Calculate inter-step intervals
    intervals = np.diff(peak_indices) / fs  # in seconds
    
    avg_step_time = float(np.mean(intervals))
    step_time_std = float(np.std(intervals))
    
    # Cadence in steps per minute
    cadence = 60.0 / avg_step_time if avg_step_time > 0 else 0.0
    
    return {
        "cadence_steps_per_min": cadence,
        "avg_step_time_sec": avg_step_time,
        "step_time_std_sec": step_time_std,
    }
