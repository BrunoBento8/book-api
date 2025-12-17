#!/usr/bin/env python3
"""
CSV to SQLite Migration Script
Migrates book data from CSV file to SQLite database
"""
import os
import sys
import pandas as pd
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine, SessionLocal, Base
from app.models.book import Book
from app.models.user import User
from app.models.api_log import APILog


def migrate_books_from_csv():
    """Migrate books from CSV to SQLite database"""

    # File paths
    csv_path = Path(__file__).parent.parent / "data" / "books.csv"

    if not csv_path.exists():
        print(f"❌ Error: CSV file not found at {csv_path}")
        return False

    print(f"📁 Reading CSV from: {csv_path}")

    # Read CSV
    try:
        df = pd.read_csv(csv_path)
        print(f"✅ Successfully read {len(df)} books from CSV")
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return False

    # Create all tables
    print("🔧 Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

    # Insert books into database
    print("📚 Inserting books into database...")
    db = SessionLocal()

    try:
        # Clear existing books (optional - for clean migration)
        db.query(Book).delete()
        db.commit()

        inserted_count = 0
        for _, row in df.iterrows():
            book = Book(
                id=int(row['id']),
                title=str(row['title']),
                price=float(row['price']),
                rating=int(row['rating']),
                availability=int(row['availability']),
                category=str(row['category']),
                image_url=str(row['image_url']) if pd.notna(row['image_url']) else None
            )
            db.add(book)
            inserted_count += 1

        db.commit()
        print(f"✅ Successfully inserted {inserted_count} books into database")

        # Verify insertion
        total_books = db.query(Book).count()
        print(f"📊 Total books in database: {total_books}")

        return True

    except Exception as e:
        print(f"❌ Error inserting books: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def print_summary():
    """Print database summary"""
    db = SessionLocal()
    try:
        total_books = db.query(Book).count()
        total_categories = db.query(Book.category).distinct().count()
        avg_price = db.query(Book.price).scalar()

        print("\n" + "=" * 50)
        print("📊 DATABASE SUMMARY")
        print("=" * 50)
        print(f"Total Books: {total_books}")
        print(f"Total Categories: {total_categories}")
        print(f"Database: {engine.url}")
        print("=" * 50)

    except Exception as e:
        print(f"❌ Error getting summary: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("\n🚀 Starting CSV to SQLite migration...")
    print("=" * 50)

    success = migrate_books_from_csv()

    if success:
        print_summary()
        print("\n✅ Migration completed successfully!")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)
