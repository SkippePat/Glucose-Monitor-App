from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, nullable=True)
    nightscout_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    glucose_readings = relationship("GlucoseReading", back_populates="user")

class GlucoseReading(Base):
    __tablename__ = "glucose_readings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, index=True)
    glucose_value = Column(Float)
    source = Column(String)  # 'nightscout' or 'manual'
    notes = Column(Text, nullable=True)
    
    user = relationship("User", back_populates="glucose_readings")
