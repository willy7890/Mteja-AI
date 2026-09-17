# In alembic/env.py
from app.core.database import Base
import app.models  # Cleanly imports everything registered in __init__.py

target_metadata = Base.metadata