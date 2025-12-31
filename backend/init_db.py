"""
Initialize database with sample users for testing
Run this script once to create initial users
"""

from app.database import SessionLocal, engine, Base
from app import models
from app.auth import get_password_hash

# Create all tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Check if users already exist
existing_users = db.query(models.User).count()

if existing_users == 0:
    print("Creating sample users...")
    
    # Create recruiter
    recruiter = models.User(
        email="recruiter@test.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test Recruiter",
        role=models.UserRole.RECRUITER,
        company="TechCorp Inc.",
        is_active=True
    )
    db.add(recruiter)
    
    # Create verifier
    verifier = models.User(
        email="verifier@test.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test Verifier",
        role=models.UserRole.VERIFIER,
        is_active=True
    )
    db.add(verifier)
    
    # Create admin
    admin = models.User(
        email="admin@test.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test Admin",
        role=models.UserRole.ADMIN,
        is_active=True
    )
    db.add(admin)
    
    db.commit()
    
    print("✅ Sample users created successfully!")
    print("\nLogin credentials:")
    print("Recruiter: recruiter@test.com / password123")
    print("Verifier: verifier@test.com / password123")
    print("Admin: admin@test.com / password123")
else:
    print(f"✅ Database already initialized with {existing_users} users")

db.close()