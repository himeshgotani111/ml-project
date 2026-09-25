"""
Cardiovascular Risk Inference Engine and Predictor Module.
Loads the pre-trained Random Forest model and StandardScaler pipeline.
"""

import os
import json
import joblib
import pandas as pd
from typing import Dict, Any, List

# Project root (2 levels up from src/models/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Canonical feature ordering expected by the trained scaler and model
ORDERED_FEATURES: List[str] = [
    "age_years",
    "gender",
    "height",
    "weight",
    "ap_hi",
    "ap_lo",
    "cholesterol",
    "gluc",
    "smoke",
    "alco",
    "active",
    "bmi",
    "pulse_pressure",
    "map_pressure"
]


class CardiovascularPredictor:
    """
    Cardiovascular Disease Predictor.
    Handles clinical feature engineering, standardization, model inference,
    risk stratification, and contextual medical factor explanation.
    """

    def __init__(self, model_dir: str = "models"):
        """
        Initializes the predictor by loading the trained model, scaler, and metadata.
        Resolves model directory robustly regardless of current working directory.
        """
        resolved_dir = self._resolve_model_dir(model_dir)

        model_path = os.path.join(resolved_dir, "trained_model.pkl")
        scaler_path = os.path.join(resolved_dir, "scaler.pkl")
        metadata_path = os.path.join(resolved_dir, "model_metadata.json")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Trained model not found at {model_path}")
        if not os.path.exists(scaler_path):
            raise FileNotFoundError(f"Scaler not found at {scaler_path}")

        # Load serialized pipeline artifacts
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)

        # Load feature names from metadata or fallback to standard features
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    self.feature_names = meta.get("features", ORDERED_FEATURES)
            except Exception:
                self.feature_names = ORDERED_FEATURES
        else:
            self.feature_names = ORDERED_FEATURES

    @staticmethod
    def _resolve_model_dir(model_dir: str) -> str:
        """
        Resolves the models directory across various runtime contexts.
        """
        candidates = [
            # 1. Direct path / relative to current working directory
            model_dir,
            # 2. Relative to project root
            os.path.join(PROJECT_ROOT, model_dir),
            # 3. Canonical project models folder
            os.path.join(PROJECT_ROOT, "models"),
        ]
        for c in candidates:
            abs_c = os.path.abspath(c)
            if os.path.isdir(abs_c) and os.path.exists(os.path.join(abs_c, "trained_model.pkl")):
                return abs_c

        # Return best candidate
        return os.path.abspath(candidates[1])

    def predict_patient(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs end-to-end cardiovascular risk prediction on a patient profile.

        Args:
            data: Dictionary containing:
                - age_years (float/int)
                - gender (int, 1=female, 2=male)
                - height (float/int, cm)
                - weight (float/int, kg)
                - ap_hi (float/int, systolic BP mmHg)
                - ap_lo (float/int, diastolic BP mmHg)
                - cholesterol (int, 1, 2, 3)
                - gluc (int, 1, 2, 3)
                - smoke (int, 0 or 1)
                - alco (int, 0 or 1)
                - active (int, 0 or 1)

        Returns:
            Dictionary formatted for the web dashboard contract:
                - prediction (int, 0 or 1)
                - prediction_label (str)
                - disease_probability (float, 0.0 - 100.0)
                - risk_level (str, "Low Risk" | "Moderate Risk" | "High Risk")
                - risk_color (str, hex color code)
                - clinical_advice (str)
                - key_factors (list of str)
                - derived_metrics (dict with bmi, pulse_pressure, map_pressure)
        """
        # Parse and sanitize inputs
        age_years = float(data.get("age_years", 50.0))
        gender = int(data.get("gender", 1))
        height = float(data.get("height", 165.0))
        weight = float(data.get("weight", 70.0))
        ap_hi = float(data.get("ap_hi", 120.0))
        ap_lo = float(data.get("ap_lo", 80.0))
        cholesterol = int(data.get("cholesterol", 1))
        gluc = int(data.get("gluc", 1))
        smoke = int(data.get("smoke", 0))
        alco = int(data.get("alco", 0))
        active = int(data.get("active", 1))

        # 1. Feature Engineering (as defined in Preprocessing & Evaluation notebooks)
        height_m = height / 100.0 if height > 0 else 1.65
        bmi = round(weight / (height_m ** 2), 2)
        pulse_pressure = round(float(ap_hi - ap_lo), 2)
        map_pressure = round(((2.0 * ap_lo) + ap_hi) / 3.0, 2)

        # 2. Assemble 14-feature DataFrame in precise training order
        feature_dict = {
            "age_years": [age_years],
            "gender": [gender],
            "height": [height],
            "weight": [weight],
            "ap_hi": [ap_hi],
            "ap_lo": [ap_lo],
            "cholesterol": [cholesterol],
            "gluc": [gluc],
            "smoke": [smoke],
            "alco": [alco],
            "active": [active],
            "bmi": [bmi],
            "pulse_pressure": [pulse_pressure],
            "map_pressure": [map_pressure]
        }
        df_features = pd.DataFrame(feature_dict, columns=self.feature_names)

        # 3. Feature Standardization
        scaled_features = self.scaler.transform(df_features)

        # 4. Model Inference
        raw_pred = int(self.model.predict(scaled_features)[0])
        raw_prob = float(self.model.predict_proba(scaled_features)[0][1])
        disease_probability = round(raw_prob * 100.0, 1)

        # 5. Risk Level & Visual UI Classification
        if disease_probability < 40.0:
            risk_level = "Low Risk"
            risk_color = "#10b981"  # Emerald green
            prediction_label = "Low Cardiovascular Risk Detected"
            clinical_advice = (
                "Clinical measurements are currently within low-risk cardiovascular limits. "
                "Continue maintaining a nutrient-dense diet, engage in at least 150 minutes of "
                "moderate physical activity weekly, and attend routine annual health screenings."
            )
        elif disease_probability < 65.0:
            risk_level = "Moderate Risk"
            risk_color = "#f59e0b"  # Amber
            prediction_label = "Moderate Cardiovascular Risk Detected"
            clinical_advice = (
                "Moderate cardiovascular risk detected. Early preventative intervention is advised: "
                "adopt a low-sodium diet, incorporate regular aerobic exercise, monitor blood pressure "
                "weekly, and consult your primary care physician for proactive management."
            )
        else:
            risk_level = "High Risk"
            risk_color = "#ef4444"  # Red
            prediction_label = "High Cardiovascular Risk Detected"
            clinical_advice = (
                "High probability of cardiovascular disease identified. Comprehensive clinical evaluation "
                "with a cardiologist is strongly recommended, including a detailed lipid panel, ECG, "
                "and personalized therapeutic blood pressure management."
            )

        # 6. Clinical Risk Factors Identification
        key_factors: List[str] = []

        # Blood pressure stratification
        if ap_hi >= 140 or ap_lo >= 90:
            key_factors.append(f"Stage 2 Hypertension (Blood Pressure: {int(ap_hi)}/{int(ap_lo)} mmHg >= 140/90)")
        elif ap_hi >= 130 or ap_lo >= 80:
            key_factors.append(f"Stage 1 Hypertension (Blood Pressure: {int(ap_hi)}/{int(ap_lo)} mmHg >= 130/80)")
        elif ap_hi >= 120 and ap_lo < 80:
            key_factors.append(f"Elevated Systolic Blood Pressure ({int(ap_hi)} mmHg)")

        # Cholesterol stratification
        if cholesterol == 3:
            key_factors.append("High Serum Cholesterol (Level 3: >= 240 mg/dL)")
        elif cholesterol == 2:
            key_factors.append("Borderline High Serum Cholesterol (Level 2: 200-239 mg/dL)")

        # Fasting Glucose stratification
        if gluc == 3:
            key_factors.append("High Fasting Glucose (Level 3: >= 126 mg/dL)")
        elif gluc == 2:
            key_factors.append("Borderline High Fasting Glucose (Level 2: 100-125 mg/dL)")

        # BMI stratification
        if bmi >= 30.0:
            key_factors.append(f"Obesity (Body Mass Index: {bmi:.1f} kg/m2 >= 30.0)")
        elif bmi >= 25.0:
            key_factors.append(f"Overweight Category (Body Mass Index: {bmi:.1f} kg/m2 >= 25.0)")

        # Pulse pressure (arterial stiffness indicator)
        if pulse_pressure > 60:
            key_factors.append(
                f"Elevated Pulse Pressure ({int(pulse_pressure)} mmHg > 60 mmHg - Arterial Stiffness Indicator)"
            )

        # Lifestyle factors
        if smoke == 1:
            key_factors.append("Active Tobacco Smoker")
        if alco == 1:
            key_factors.append("Regular Alcohol Intake")
        if active == 0:
            key_factors.append("Sedentary Lifestyle (Low Physical Activity)")

        # Age group
        if age_years >= 55:
            key_factors.append(f"Elevated Age Category ({int(age_years)} years old >= 55)")

        if not key_factors:
            key_factors.append("All primary physiological and lifestyle indicators are within standard reference ranges.")

        # 7. Formulate structured response
        return {
            "prediction": raw_pred,
            "prediction_label": prediction_label,
            "disease_probability": disease_probability,
            "risk_level": risk_level,
            "risk_color": risk_color,
            "clinical_advice": clinical_advice,
            "key_factors": key_factors,
            "derived_metrics": {
                "bmi": round(float(bmi), 1),
                "pulse_pressure": round(float(pulse_pressure), 1),
                "map_pressure": round(float(map_pressure), 1)
            }
        }
