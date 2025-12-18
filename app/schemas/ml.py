from pydantic import BaseModel, Field
from typing import List, Dict, Any


class MLFeaturesResponse(BaseModel):
    """Response schema for ML features"""
    features: List[Dict[str, Any]]
    feature_names: List[str]
    total_samples: int
    description: str


class TrainingDataResponse(BaseModel):
    """Response schema for training data"""
    data: List[Dict[str, Any]]
    total_samples: int
    features: List[str]
    target_variable: str
    description: str


class PredictionItem(BaseModel):
    """Schema for a single prediction"""
    book_id: int = Field(..., description="Book ID")
    prediction_score: float = Field(..., ge=0, le=1, description="Prediction score (0-1)")
    model_version: str = Field(..., description="ML model version used")
    metadata: Dict[str, Any] | None = Field(None, description="Additional prediction metadata")


class PredictionRequest(BaseModel):
    """Schema for submitting predictions"""
    predictions: List[PredictionItem]
    model_name: str = Field(..., description="Name of the ML model")
    timestamp: str | None = None


class PredictionResponse(BaseModel):
    """Response schema for predictions submission"""
    status: str
    message: str
    predictions_received: int
    model_name: str
