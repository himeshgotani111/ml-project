"""
Clinical helper functions and preset patient profiles.
"""

from typing import List, Dict, Any


def get_sample_patients() -> List[Dict[str, Any]]:
    """
    Returns preset clinical patient profiles for testing and dashboard demonstration.
    
    Profiles match the presets configured in the frontend dashboard:
    1. Arjun Patel - Low Risk Profile (32 years old, active, normal metrics)
    2. Priya Sharma - Moderate Risk Profile (50 years old, borderline cholesterol/BP)
    3. Ramesh Verma - High Risk Profile (62 years old, hypertension, smoker, high cholesterol)
    """
    return [
        {
            "name": "Arjun Patel",
            "age_years": 32,
            "gender": 2,  # Male
            "height": 175.0,
            "weight": 70.0,
            "ap_hi": 115.0,
            "ap_lo": 75.0,
            "cholesterol": 1,  # Normal (<200 mg/dL)
            "gluc": 1,         # Normal (<100 mg/dL)
            "smoke": 0,        # Non-smoker
            "alco": 0,         # No alcohol
            "active": 1,       # Physically active
            "description": "Low Risk Sample, 32y"
        },
        {
            "name": "Priya Sharma",
            "age_years": 50,
            "gender": 1,  # Female
            "height": 162.0,
            "weight": 72.0,
            "ap_hi": 132.0,
            "ap_lo": 86.0,
            "cholesterol": 2,  # Above Normal (200-239 mg/dL)
            "gluc": 1,         # Normal (<100 mg/dL)
            "smoke": 0,        # Non-smoker
            "alco": 0,         # No alcohol
            "active": 1,       # Physically active
            "description": "Moderate Risk Sample, 50y"
        },
        {
            "name": "Ramesh Verma",
            "age_years": 62,
            "gender": 2,  # Male
            "height": 168.0,
            "weight": 88.0,
            "ap_hi": 158.0,
            "ap_lo": 98.0,
            "cholesterol": 3,  # Well Above Normal (≥240 mg/dL)
            "gluc": 2,         # Above Normal (100-125 mg/dL)
            "smoke": 1,        # Active smoker
            "alco": 1,         # Regular alcohol
            "active": 0,       # Sedentary
            "description": "High Risk Sample, 62y"
        }
    ]
