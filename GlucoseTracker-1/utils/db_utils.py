from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models.models import User, GlucoseReading
from typing import List, Optional

class DatabaseManager:
    @staticmethod
    def get_or_create_user(db: Session, email: str, nightscout_url: str, phone_number: Optional[str] = None) -> Optional[User]:
        """Get existing user or create a new one"""
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                # Create new user with constructor
                user = User(
                    email=email,
                    nightscout_url=nightscout_url,
                    phone_number=phone_number if phone_number else None
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            else:
                # Update existing user with new data if provided
                if nightscout_url and nightscout_url != "https://your-nightscout-url.herokuapp.com":
                    setattr(user, 'nightscout_url', nightscout_url)
                if phone_number:
                    setattr(user, 'phone_number', phone_number)
                db.commit()
                db.refresh(user)
            return user
        except Exception as e:
            db.rollback()
            raise Exception(f"Database error: {str(e)}")

    @staticmethod
    def save_glucose_reading(
        db: Session,
        user,  # Accept user object instead of user_id
        glucose_value: float,
        timestamp: datetime,
        source: str,
        notes: Optional[str] = None
    ) -> Optional[GlucoseReading]:
        """Save a new glucose reading"""
        try:
            # Create reading with dictionary to avoid attribute assignment issues
            reading = GlucoseReading(
                user_id=user.id,
                glucose_value=glucose_value,
                timestamp=timestamp,
                source=source,
                notes=notes
            )
                
            db.add(reading)
            db.commit()
            db.refresh(reading)
            return reading
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to save glucose reading: {str(e)}")

    @staticmethod
    def get_user_readings(
        db: Session,
        user_id: int,
        hours: int = 24
    ) -> List[GlucoseReading]:
        """Get user's glucose readings for the specified time period"""
        try:
            since = datetime.utcnow() - timedelta(hours=hours)
            return db.query(GlucoseReading).filter(
                GlucoseReading.user_id == user_id,
                GlucoseReading.timestamp >= since
            ).order_by(GlucoseReading.timestamp.desc()).all()
        except Exception as e:
            raise Exception(f"Failed to fetch glucose readings: {str(e)}")