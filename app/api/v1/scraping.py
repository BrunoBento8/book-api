from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
import subprocess
import sys
from pathlib import Path
from app.database import get_db
from app.models.user import User
from app.utils.security import get_current_admin_user
from app.services.stats_service import stats_service

router = APIRouter()


def run_scraper_task():
    """Background task to run the web scraper"""
    try:
        # Get the path to the scraping script
        script_path = Path(__file__).parent.parent.parent.parent / "scripts" / "scraping.py"

        # Run the scraping script
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )

        if result.returncode == 0:
            print("✅ Scraper executed successfully")
            print(result.stdout)

            # Run migration to update database
            migration_script = Path(__file__).parent.parent.parent.parent / "scripts" / "migrate_csv_to_db.py"
            migration_result = subprocess.run(
                [sys.executable, str(migration_script)],
                capture_output=True,
                text=True,
                timeout=120
            )

            if migration_result.returncode == 0:
                print("✅ Database updated successfully")
                # Invalidate stats cache
                stats_service.invalidate_cache()
            else:
                print(f"❌ Error updating database: {migration_result.stderr}")

        else:
            print(f"❌ Error running scraper: {result.stderr}")

    except subprocess.TimeoutExpired:
        print("❌ Scraper timed out after 5 minutes")
    except Exception as e:
        print(f"❌ Error running scraper: {str(e)}")


@router.post("/scraping/trigger")
async def trigger_scraper(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Trigger web scraper to update book data (Admin Only)

    This endpoint is protected and requires admin privileges.
    The scraper runs in the background and updates the database
    with the latest book data from books.toscrape.com.

    **Authentication Required:**
    - Must be logged in as an admin user
    - Include access token in Authorization header:
      `Authorization: Bearer your_access_token`

    **Process:**
    1. Runs the web scraper (scripts/scraping.py)
    2. Updates CSV with new data
    3. Re-runs migration to update database
    4. Invalidates statistics cache

    **Returns:**
    - 202 Accepted: Scraper job started
    - 403 Forbidden: User is not an admin
    - 401 Unauthorized: Invalid or missing token
    """

    # Add scraping task to background
    background_tasks.add_task(run_scraper_task)

    return {
        "status": "accepted",
        "message": "Scraper triggered successfully. Running in background.",
        "triggered_by": current_user.username,
        "note": "This may take a few minutes to complete. Check logs for progress."
    }


@router.get("/scraping/status")
async def get_scraper_status(
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get scraper status (Admin Only)

    Returns information about the last scraping operation.
    """
    return {
        "status": "info",
        "message": "Scraper status endpoint - implementation pending",
        "note": "Check application logs for detailed scraper execution history"
    }


@router.post("/scraping/import-csv")
async def import_csv_to_database(
    force: bool = False,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Import books from CSV to database (Admin Only)

    Forces reimportation of books from the existing CSV file.
    Useful when the database is empty but the CSV exists.

    **Parameters:**
    - **force**: If True, deletes existing books and reimports. Default: False

    **Authentication Required:**
    - Must be logged in as an admin user
    - Include access token in Authorization header

    **Returns:**
    - 200 OK: Import successful
    - 400 Bad Request: CSV file not found
    - 403 Forbidden: User is not an admin
    """
    import pandas as pd
    from app.models.book import Book

    try:
        # Get CSV path
        csv_path = Path(__file__).parent.parent.parent.parent / "data" / "books.csv"

        if not csv_path.exists():
            raise HTTPException(
                status_code=400,
                detail=f"CSV file not found at {csv_path}. Please run the scraper first."
            )

        # Read CSV
        df = pd.read_csv(csv_path)
        books_in_csv = len(df)

        # Check existing books
        existing_count = db.query(Book).count()

        # If force=True, delete all existing books
        if force and existing_count > 0:
            db.query(Book).delete()
            db.commit()
            print(f"🗑️  Deleted {existing_count} existing books")
            existing_count = 0

        # If books already exist and not forcing, return info
        if existing_count > 0:
            return {
                "status": "skipped",
                "message": f"Database already contains {existing_count} books",
                "csv_books": books_in_csv,
                "note": "Use force=true parameter to delete and reimport all books"
            }

        # Import books from CSV
        imported_count = 0
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
            imported_count += 1

        db.commit()

        # Invalidate stats cache
        stats_service.invalidate_cache()

        return {
            "status": "success",
            "message": f"Successfully imported {imported_count} books from CSV",
            "imported": imported_count,
            "csv_books": books_in_csv,
            "triggered_by": current_user.username
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error importing CSV: {str(e)}"
        )
