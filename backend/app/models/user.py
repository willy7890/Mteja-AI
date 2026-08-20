# user SQLAlchemy model for MTEJA AI
from sqlalchemy.orm import Mapped,mapped_column,Datetime,uuid,DeclarativeBase,relationship
from sqlalchemy import String,Datetime,ForeignKey,Enum,func,UniqueConstraint
from datetime import datetime
import enum,uuid
from app.core.database import Base

# Defines table schema, relationships, and multi-tenant organization_id
class user(Base):
    __tablename__="user"
    __table_args__=(UniqueConstraint("user_id",name="user"),)
    #columns
    id:Mapped[]= mapped_column()
    name:
    email:
    address:
    phone_number:
    password_hash: