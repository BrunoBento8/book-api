from sqlalchemy import Column, Integer, String, Float, Index
from app.database import Base


class Book(Base):
    """Book model representing books from the CSV data"""

    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    price = Column(Float, nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    availability = Column(Integer, nullable=False, default=0)  # Stock count
    category = Column(String(100), nullable=False, index=True)
    image_url = Column(String(1000), nullable=True)

    # Composite indexes for performance optimization
    __table_args__ = (
        Index('idx_category_rating', 'category', 'rating'),
        Index('idx_price_rating', 'price', 'rating'),
    )

    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}', price={self.price})>"
