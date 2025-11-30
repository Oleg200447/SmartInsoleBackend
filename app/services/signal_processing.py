"""Signal processing functions for insole sensor data"""

from typing import Dict, List, Any
import numpy as np
from scipy.signal import butter, filtfilt

from app.config import (
    SAMPLE_RATE,
    TARGET_RATE,
    LOWPASS_CUTOFF,
    FILTER_ORDER,
    SMOOTHING_WINDOW,
    NUM_CHANNELS,
)


def butter_lowpass_filter(
    data: np.ndarray, 
    cutoff: float = LOWPASS_CUTOFF, 
    fs: float = SAMPLE_RATE, 
    order: int = FILTER_ORDER
) -> np.ndarray:
    """
    Apply Butterworth lowpass filter to signal data.
    
    Args:
        data: Input signal array
        cutoff: Cutoff frequency in Hz
        fs: Sample rate in Hz
        order: Filter order
        
    Returns:
        Filtered signal array
    """
    if len(data) < order * 3:
        # Not enough data points for filtering
        return data
        
    nyq = 0.5 * fs  # Nyquist frequency
    normal_cutoff = cutoff / nyq
    
    # Design the filter
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    
    # Apply filter without phase distortion
    filtered = filtfilt(b, a, data)
    return filtered


def decimate_signal(
    signal: np.ndarray, 
    fs_old: float = SAMPLE_RATE, 
    fs_new: float = TARGET_RATE
) -> np.ndarray:
    """
    Downsample signal by decimation factor.
    
    Args:
        signal: Input signal array
        fs_old: Original sample rate
        fs_new: Target sample rate
        
    Returns:
        Decimated signal array
    """
    decim_factor = int(round(fs_old / fs_new))
    if decim_factor <= 1:
        return signal
    return signal[::decim_factor]


def prep_signal(signal: np.ndarray, window: int = SMOOTHING_WINDOW) -> np.ndarray:
    """
    Prepare signal by removing baseline and normalizing direction.
    
    This function:
    1. Pads the signal for edge handling
    2. Computes moving average (baseline)
    3. Subtracts baseline from signal
    4. Normalizes direction based on max/min amplitude
    
    Args:
        signal: Input signal array
        window: Smoothing window size (should be odd)
        
    Returns:
        Processed signal with baseline removed
    """
    if len(signal) < window:
        # Not enough data for smoothing
        return signal - np.mean(signal)
    
    # Pad signal for edge handling
    signal_padded = np.pad(signal, window // 2, mode='edge')
    
    # Compute moving average (baseline)
    smooth = np.convolve(signal_padded, np.ones(window) / window, mode='same')
    
    # Extract detail (signal - baseline)
    detail = (signal_padded - smooth)[window // 2:-window // 2 + 1]
    
    # Ensure correct length
    if len(detail) > len(signal):
        detail = detail[:len(signal)]
    elif len(detail) < len(signal):
        detail = np.pad(detail, (0, len(signal) - len(detail)), mode='edge')
    
    # Normalize direction based on amplitude
    if np.abs(np.max(detail)) > np.abs(np.min(detail)):
        return detail
    else:
        return -detail


def process_channels(readings: List[Dict[str, Any]]) -> Dict[str, np.ndarray]:
    """
    Process all 8 channels from raw sensor readings.
    
    Pipeline:
    1. Extract channel data
    2. Apply lowpass filter
    3. Decimate to target rate
    
    Args:
        readings: List of sensor reading dictionaries
        
    Returns:
        Dictionary with processed arrays for each channel (ch0-ch7)
    """
    if not readings:
        return {f"ch{i}": np.array([]) for i in range(NUM_CHANNELS)}
    
    # Extract raw channel data
    raw_channels = {}
    for i in range(NUM_CHANNELS):
        channel_name = f"ch{i}"
        raw_channels[channel_name] = np.array([r[channel_name] for r in readings], dtype=float)
    
    # Process each channel
    processed_channels = {}
    for channel_name, raw_data in raw_channels.items():
        if len(raw_data) == 0:
            processed_channels[channel_name] = np.array([])
            continue
            
        # Apply lowpass filter
        filtered = butter_lowpass_filter(raw_data)
        
        # Decimate to target rate
        decimated = decimate_signal(filtered)
        
        processed_channels[channel_name] = decimated
    
    return processed_channels


def generate_timestamps(num_samples: int, fs: float = TARGET_RATE) -> np.ndarray:
    """
    Generate timestamp array for processed signals.
    
    Args:
        num_samples: Number of samples
        fs: Sample rate
        
    Returns:
        Array of timestamps in seconds
    """
    return np.arange(num_samples) / fs


def extract_channels_array(readings: List[Dict[str, Any]]) -> np.ndarray:
    """
    Extract all channels as 2D numpy array.
    
    Args:
        readings: List of sensor reading dictionaries
        
    Returns:
        2D array of shape (num_readings, 8)
    """
    if not readings:
        return np.array([]).reshape(0, NUM_CHANNELS)
    
    data = []
    for r in readings:
        row = [r[f"ch{i}"] for i in range(NUM_CHANNELS)]
        data.append(row)
    
    return np.array(data, dtype=float)
