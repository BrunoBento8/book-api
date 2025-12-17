#!/usr/bin/env python3
"""
Create Admin User Script
Creates an admin user for the application
"""
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, Base, engine
from app.models.user import User
from app.utils.security import get_password_hash
from app.config import settings


def create_admin_user():
    """Create admin user from environment variables"""

    print("🔧 Creating database tables if not exist...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.username == settings.ADMIN_USERNAME).first()

        if existing_admin:
            print(f"⚠️  Admin user '{settings.ADMIN_USERNAME}' already exists!")
            print(f"   User ID: {existing_admin.id}")
            print(f"   Email: {existing_admin.email}")
            print(f"   Is Admin: {existing_admin.is_admin}")
            print(f"   Is Active: {existing_admin.is_active}")
            return

        # Create new admin user
        # Truncate password to 72 bytes for bcrypt compatibility
        password = settings.ADMIN_PASSWORD[:72]
        admin = User(
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            hashed_password=get_password_hash(password),
            is_admin=True,
            is_active=True
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("\n" + "=" * 50)
        print("✅ Admin user created successfully!")
        print("=" * 50)
        print(f"Username: {admin.username}")
        print(f"Email: {admin.email}")
        print(f"Password: {settings.ADMIN_PASSWORD}")
        print(f"Is Admin: {admin.is_admin}")
        print(f"User ID: {admin.id}")
        print("=" * 50)
        print("\n💡 You can now login with these credentials:")
        print(f"   POST /api/v1/auth/login")
        print(f"   username={admin.username}&password={settings.ADMIN_PASSWORD}")
        print()

    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print("\n🚀 Admin User Creation Script")
    print("=" * 50)
    create_admin_user()
