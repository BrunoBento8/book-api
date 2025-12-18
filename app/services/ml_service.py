from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.models.book import Book
import pandas as pd


class MLService:
    """Service class for ML data preparation and feature engineering"""

    @staticmethod
    def prepare_ml_features(db: Session, limit: int = 1000) -> Dict[str, Any]:
        """
        Prepare ML-ready features from book data

        Includes:
        - One-hot encoded categories
        - Normalized price (0-1 scale)
        - Rating as numerical feature
        - Availability buckets

        Returns:
            Dictionary with features array and feature names
        """
        books = db.query(Book).limit(limit).all()

        if not books:
            return {
                "features": [],
                "feature_names": [],
                "total_samples": 0
            }

        # Convert to pandas for easier processing
        data = []
        for book in books:
            data.append({
                "id": book.id,
                "price": book.price,
                "rating": book.rating,
                "availability": book.availability,
                "category": book.category
            })

        df = pd.DataFrame(data)

        # Feature engineering
        # 1. Normalize price (min-max scaling)
        price_min, price_max = df['price'].min(), df['price'].max()
        df['price_normalized'] = (df['price'] - price_min) / (price_max - price_min) if price_max > price_min else 0

        # 2. Rating as numerical (already 1-5)
        df['rating_numerical'] = df['rating']

        # 3. Availability buckets
        df['availability_bucket'] = pd.cut(
            df['availability'],
            bins=[-1, 0, 10, 20, float('inf')],
            labels=['out_of_stock', 'low', 'medium', 'high']
        )

        # 4. One-hot encode categories
        category_dummies = pd.get_dummies(df['category'], prefix='category')

        # 5. One-hot encode availability buckets
        availability_dummies = pd.get_dummies(df['availability_bucket'], prefix='avail')

        # Combine all features
        features_df = pd.concat([
            df[['id', 'price_normalized', 'rating_numerical']],
            category_dummies,
            availability_dummies
        ], axis=1)

        # Convert to list of dictionaries
        features_list = features_df.to_dict('records')
        feature_names = list(features_df.columns)

        return {
            "features": features_list,
            "feature_names": feature_names,
            "total_samples": len(features_list)
        }

    @staticmethod
    def export_training_data(db: Session, format: str = "json") -> Dict[str, Any]:
        """
        Export complete dataset for ML model training

        Args:
            db: Database session
            format: Export format (json or dict)

        Returns:
            Dictionary with training data and metadata
        """
        books = db.query(Book).all()

        data = []
        for book in books:
            data.append({
                "id": book.id,
                "title": book.title,
                "price": book.price,
                "rating": book.rating,  # This can be used as target variable
                "availability": book.availability,
                "category": book.category,
                "image_url": book.image_url
            })

        df = pd.DataFrame(data)

        # Feature columns (everything except target)
        feature_columns = ['id', 'price', 'availability', 'category']
        target_variable = 'rating'

        return {
            "data": data,
            "total_samples": len(data),
            "features": feature_columns,
            "target_variable": target_variable,
            "description": "Complete dataset for training ML models. Rating can be used as target for regression/classification."
        }

    @staticmethod
    def store_predictions(db: Session, predictions: List[Dict], model_name: str) -> int:
        """
        Store ML predictions for future use

        Note: This is a placeholder. In production, you'd want to create
        a Predictions table to store these.

        Args:
            db: Database session
            predictions: List of prediction dictionaries
            model_name: Name of the ML model

        Returns:
            Number of predictions stored
        """
        # For now, just return the count
        # In production: Create Prediction model and save to DB
        print(f"📊 Received {len(predictions)} predictions from model: {model_name}")
        for pred in predictions[:5]:  # Log first 5
            print(f"  Book {pred['book_id']}: score={pred['prediction_score']:.3f}")

        return len(predictions)


# Create singleton instance
ml_service = MLService()
