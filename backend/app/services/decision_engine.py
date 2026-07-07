from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class DecisionConfig(BaseModel):
    """
    Configuration rules for the Decision Engine.
    All values are configurable without changing the core logic.
    Provides modular rule adjustments for quality, risk, and shelf life.
    """
    
    # ---------------------------------------------------------
    # Rule Set 1: Quality Score Baseline Rules
    # ---------------------------------------------------------
    class_scores: Dict[str, int] = Field(
        default={"A": 95, "B": 80, "C": 60, "D": 30},
        description="Base quality score out of 100 assigned strictly based on the ML predicted class."
    )
    
    # ---------------------------------------------------------
    # Rule Set 2: Confidence Threshold Rules
    # ---------------------------------------------------------
    confidence_high_threshold: float = Field(
        default=0.85,
        description="Probability threshold to classify a prediction as High Confidence."
    )
    confidence_medium_threshold: float = Field(
        default=0.65,
        description="Probability threshold to classify a prediction as Medium Confidence. Below this is Low."
    )
    
    # ---------------------------------------------------------
    # Rule Set 3: Shelf Life Estimation Rules
    # ---------------------------------------------------------
    base_shelf_life_days: Dict[str, int] = Field(
        default={"A": 14, "B": 7, "C": 3, "D": 0},
        description="Base shelf life in days estimated purely from the predicted class."
    )
    shelf_life_confidence_penalty: int = Field(
        default=2,
        description="Days to subtract from estimated shelf life if the model confidence is Low."
    )
    shelf_life_anomaly_penalty: int = Field(
        default=3,
        description="Days to subtract from estimated shelf life if a raw sensor anomaly is detected."
    )

    # ---------------------------------------------------------
    # Rule Set 4: Business Risk Classification Rules
    # ---------------------------------------------------------
    high_risk_classes: List[str] = Field(
        default=["D"],
        description="Classes that immediately trigger a High Business Risk classification."
    )
    medium_risk_classes: List[str] = Field(
        default=["C"],
        description="Classes that immediately trigger a Medium Business Risk classification."
    )
    sensor_warning_threshold: float = Field(
        default=2.0, 
        description="If any raw sensor reading exceeds this value, it triggers a hardware anomaly penalty."
    )
    shap_negative_impact_threshold: float = Field(
        default=0.1,
        description="If a top SHAP feature has a negative impact greater than this magnitude, elevate risk."
    )


class BusinessDecision(BaseModel):
    """
    Business-oriented recommendation output schema.
    """
    quality_score: int
    confidence: str
    business_risk: str
    estimated_shelf_life: str
    recommendation: str
    warning: Optional[str] = None
    reasoning: List[str]


class DecisionEngine:
    """
    Transforms raw ML model outputs into actionable business recommendations.
    Follows Clean Architecture by isolating configurable business rules from the main ML pipeline.
    """
    
    def __init__(self, config: Optional[DecisionConfig] = None):
        """Initialize the decision engine with configurable modular rules."""
        self.config = config or DecisionConfig()

    def generate_decision(
        self,
        predicted_class: str,
        prediction_probabilities: Dict[str, float],
        shap_feature_importance: List[Dict[str, Any]],
        sensor_values: List[float]
    ) -> BusinessDecision:
        """
        Generate a comprehensive business decision JSON output.
        """
        reasoning = []
        
        # ---------------------------------------------------------
        # Phase 1: Confidence Evaluation
        # ---------------------------------------------------------
        class_prob = prediction_probabilities.get(predicted_class, 0.5)
        
        if class_prob >= self.config.confidence_high_threshold:
            confidence_level = "High"
        elif class_prob >= self.config.confidence_medium_threshold:
            confidence_level = "Medium"
        else:
            confidence_level = "Low"
            reasoning.append(f"Model confidence is low ({class_prob:.1%}). Manual quality inspection is recommended.")

        # ---------------------------------------------------------
        # Phase 2: Quality Score Calculation
        # ---------------------------------------------------------
        base_score = self.config.class_scores.get(predicted_class, 50)
        
        # The final quality score is a weighted combination of the base class score (80%) 
        # and the exact probability variance (20%) to provide a continuous 0-100 scale.
        quality_score = int(base_score * (0.8 + 0.2 * class_prob))
        quality_score = max(0, min(100, quality_score))
        reasoning.append(f"Calculated base quality score of {quality_score}/100 based on class '{predicted_class}' and confidence.")

        # ---------------------------------------------------------
        # Phase 3: Hardware Anomaly Detection (Sensors)
        # ---------------------------------------------------------
        sensor_anomaly = False
        if sensor_values and max(sensor_values) > self.config.sensor_warning_threshold:
            sensor_anomaly = True
            
        # ---------------------------------------------------------
        # Phase 4: Dynamic Shelf Life Estimation
        # ---------------------------------------------------------
        # Rule: Base shelf life is determined by class.
        # Penalties are applied dynamically based on confidence and hardware anomalies.
        base_days = self.config.base_shelf_life_days.get(predicted_class, 0)
        penalty = 0
        
        if confidence_level == "Low":
            penalty += self.config.shelf_life_confidence_penalty
            reasoning.append(f"Reduced shelf life by {self.config.shelf_life_confidence_penalty} days due to low prediction confidence.")
            
        if sensor_anomaly:
            penalty += self.config.shelf_life_anomaly_penalty
            reasoning.append(f"Reduced shelf life by {self.config.shelf_life_anomaly_penalty} days due to anomalous peak sensor readings.")
            
        final_shelf_life_days = max(0, base_days - penalty)
        shelf_life = f"{final_shelf_life_days}+ days" if final_shelf_life_days >= 10 else f"{final_shelf_life_days} days"

        # ---------------------------------------------------------
        # Phase 5: Business Risk & Recommendation Formulation
        # ---------------------------------------------------------
        # Baseline assumption: Product is healthy
        risk = "Low"
        recommendation = "Premium retail distribution. High nutritional value."
        warning = None
        
        # Rule 5.1: Prediction Class Priority
        # If the class falls into a predefined High/Medium risk bucket, override the baseline.
        if predicted_class in self.config.high_risk_classes:
            risk = "High"
            recommendation = "Discard or route to low-grade processing (e.g., compost, animal feed)."
            warning = "Critical spoilage detected. Not suitable for human consumption."
            reasoning.append(f"High Risk: Class '{predicted_class}' indicates critical degradation.")
        elif predicted_class in self.config.medium_risk_classes:
            risk = "Medium"
            recommendation = "Immediate local sale or route to juice extraction."
            reasoning.append("Medium Risk: Product is aging. Expedite distribution to avoid spoilage.")
            
        # Rule 5.2: Confidence Penalty
        # If the model is uncertain on a "Low" risk product, elevate to Medium risk to ensure human oversight.
        if confidence_level == "Low" and risk == "Low":
            risk = "Medium"
            recommendation = "Route to standard retail. Manual inspection advised."
            warning = "Low model confidence. Do not route to premium retail without manual inspection."
            reasoning.append("Elevated risk to Medium due to low model confidence on premium product.")
            
        # Rule 5.3: Sensor Anomaly Penalty
        # If a hardware anomaly fired, escalate the risk severity by one tier.
        if sensor_anomaly and risk != "High":
            risk = "Medium" if risk == "Low" else "High"
            warning = "Anomalous sensor readings detected. Accelerated spoilage likely."
            reasoning.append(f"Elevated risk to {risk} due to sensor anomaly exceeding threshold ({self.config.sensor_warning_threshold}).")
            
        # Rule 5.4: SHAP Explanatory Analysis
        # Hook into the XAI pipeline. If the most important feature negatively impacts the score
        # beyond a defined magnitude, it implies underlying chemical instability.
        if shap_feature_importance and len(shap_feature_importance) > 0:
            top_feat = shap_feature_importance[0]
            feature_name = top_feat.get("feature_name", "Unknown feature")
            impact = top_feat.get("impact", "neutral")
            absolute_importance = float(top_feat.get("absolute_importance", 0.0))
            
            if impact == "decrease" and absolute_importance > self.config.shap_negative_impact_threshold:
                if risk == "Low":
                    risk = "Medium"
                    warning = f"Chemical instability detected: {feature_name} is negatively impacting freshness."
                    recommendation = "Downgrade from premium retail. Monitor closely."
                    reasoning.append(f"Elevated risk to Medium because {feature_name} negatively impacts the prediction significantly (magnitude: {absolute_importance:.2f}).")
                else:
                    reasoning.append(f"Note: {feature_name} is a major negative factor accelerating spoilage.")
            elif impact == "increase":
                reasoning.append(f"Primary driver for this prediction is {feature_name} (positive impact).")
            
        return BusinessDecision(
            quality_score=quality_score,
            confidence=confidence_level,
            business_risk=risk,
            estimated_shelf_life=shelf_life,
            recommendation=recommendation,
            warning=warning,
            reasoning=reasoning
        )
