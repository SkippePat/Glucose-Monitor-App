from .base import Base, engine, get_db
from .models import User, GlucoseReading

def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)

# Initialize database tables
init_db()