from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.ml import (
    MLFeaturesResponse,
    TrainingDataResponse,
    PredictionRequest,
    PredictionResponse
)
from app.services.ml_service import ml_service
from datetime import datetime

router = APIRouter()


@router.get("/ml/features", response_model=MLFeaturesResponse)
async def get_ml_features(
    limit: int = Query(1000, ge=1, le=1000, description="Maximum number of samples"),
    db: Session = Depends(get_db)
):
    """
    Get ML-ready features for model training/inference

    **Feature Engineering Applied:**
    - Price normalization (min-max scaling to 0-1)
    - Rating as numerical feature (1-5)
    - Availability bucketing (out_of_stock, low, medium, high)
    - One-hot encoding for categories
    - One-hot encoding for availability buckets

    **Use Cases:**
    - Training recommendation models
    - Feature analysis and EDA
    - Model evaluation datasets

    **Returns:**
    - `features`: Array of feature vectors
    - `feature_names`: List of feature column names
    - `total_samples`: Number of samples returned

    **Example:**
    ```python
    import requests
    import pandas as pd

    response = requests.get("http://localhost:8000/api/v1/ml/features")
    data = response.json()

    # Convert to pandas DataFrame
    df = pd.DataFrame(data['features'])
    X = df[data['feature_names']]
    ```
    """
    result = ml_service.prepare_ml_features(db, limit)

    return MLFeaturesResponse(
        features=result["features"],
        feature_names=result["feature_names"],
        total_samples=result["total_samples"],
        description="ML-ready features with normalization and encoding applied"
    )


@router.get("/ml/training-data", response_model=TrainingDataResponse)
async def get_training_data(
    format: str = Query("json", regex="^(json|csv)$", description="Export format"),
    db: Session = Depends(get_db)
):
    """
    Export complete dataset for ML model training

    **Dataset Information:**
    - All book records with original values
    - Target variable: `rating` (1-5 scale)
    - Features: price, availability, category
    - Suitable for both regression and classification tasks

    **Supported Formats:**
    - `json` (default): Returns JSON array of objects
    - `csv`: Returns CSV formatted data (future enhancement)

    **Use Cases:**
    - Training collaborative filtering models
    - Building recommendation systems
    - Predicting book ratings
    - Category-based models

    **Example Usage:**
    ```python
    import requests
    import pandas as pd

    # Get training data
    response = requests.get("http://localhost:8000/api/v1/ml/training-data")
    data = response.json()

    # Convert to DataFrame
    df = pd.DataFrame(data['data'])

    # Separate features and target
    X = df[data['features']]
    y = df[data['target_variable']]

    # Train model
    from sklearn.ensemble import RandomForestRegressor
    model = RandomForestRegressor()
    model.fit(X, y)
    ```
    """
    result = ml_service.export_training_data(db, format)

    if format == "csv":
        # Future enhancement: return CSV response
        import pandas as pd
        df = pd.DataFrame(result["data"])
        csv_content = df.to_csv(index=False)

        return JSONResponse(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=books_training_data_{datetime.now().strftime('%Y%m%d')}.csv"
            }
        )

    return TrainingDataResponse(**result)


@router.post("/ml/predictions", response_model=PredictionResponse)
async def submit_predictions(
    prediction_request: PredictionRequest,
    db: Session = Depends(get_db)
):
    """
    Submit ML model predictions for storage and analysis

    This endpoint allows ML models to send their predictions back to the API
    for storage, monitoring, and integration with the recommendation system.

    **Request Body:**
    ```json
    {
      "model_name": "collaborative_filtering_v1",
      "predictions": [
        {
          "book_id": 1,
          "prediction_score": 0.85,
          "model_version": "1.0.0",
          "metadata": {"confidence": "high"}
        }
      ],
      "timestamp": "2025-12-17T10:30:00Z"
    }
    ```

    **Prediction Score:**
    - Must be between 0 and 1
    - Represents recommendation confidence or predicted rating (normalized)
    - Higher scores indicate stronger recommendations

    **Use Cases:**
    - Storing model predictions for A/B testing
    - Building hybrid recommendation systems
    - Monitoring model performance
    - Creating feedback loops

    **Future Enhancements:**
    - Store predictions in database (Prediction model)
    - Calculate prediction accuracy metrics
    - Compare multiple model performances
    - Generate recommendation lists based on scores
    """
    try:
        count = ml_service.store_predictions(
            db,
            [pred.model_dump() for pred in prediction_request.predictions],
            prediction_request.model_name
        )

        return PredictionResponse(
            status="success",
            message="Predictions received and stored successfully",
            predictions_received=count,
            model_name=prediction_request.model_name
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error storing predictions: {str(e)}"
        )
