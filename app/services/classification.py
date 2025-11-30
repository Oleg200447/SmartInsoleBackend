"""Mock classification service for activity detection"""

import random
from typing import Tuple

from app.config import ACTIVITIES


def classify_activity() -> Tuple[str, float]:
    """
    Mock classifier that returns random activity and confidence.
    
    In a real implementation, this would:
    1. Extract features from signals (percentile values per channel per foot)
    2. Feed features to a trained logistic regression model
    3. Return predicted class and probability
    
    Returns:
        Tuple of (activity_name, confidence_score)
    """
    # Randomly select an activity
    activity = random.choice(ACTIVITIES)
    
    # Generate random confidence between 0.6 and 0.95
    confidence = random.uniform(0.6, 0.95)
    
    return activity, confidence


def get_activity_icon(activity: str) -> str:
    """
    Get emoji icon for activity type.
    
    Args:
        activity: Activity name
        
    Returns:
        Emoji string
    """
    icons = {
        "walking": "🚶",
        "sitting": "🪑",
        "running": "🏃",
    }
    return icons.get(activity, "❓")


def get_activity_description(activity: str) -> str:
    """
    Get description for activity type.
    
    Args:
        activity: Activity name
        
    Returns:
        Description string
    """
    descriptions = {
        "walking": "Normal walking gait detected",
        "sitting": "Stationary or sitting position detected",
        "running": "Running or fast movement detected",
    }
    return descriptions.get(activity, "Unknown activity")


# Placeholder for future implementation
def extract_classification_features(
    left_channels: dict,
    right_channels: dict,
    percentile_bins: int = 10
) -> list:
    """
    Extract features for classification model.
    
    This is a placeholder for future implementation.
    Features would be extracted as percentile values for each channel.
    
    Args:
        left_channels: Processed channels for left foot
        right_channels: Processed channels for right foot
        percentile_bins: Number of percentile bins (0-10, 10-20, etc.)
        
    Returns:
        List of feature values
    """
    # TODO: Implement actual feature extraction
    # For each channel (8) × each foot (2) × each percentile bin (10)
    # Total features = 8 × 2 × 10 = 160 features
    return []
