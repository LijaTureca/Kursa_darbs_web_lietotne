#database.py
import numpy as np
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from contextlib import contextmanager

@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
        
# PostgreSQL
DATABASE_URL = "postgresql://azureuser:azure@52.233.181.73:5432/predictions"
#DATABASE_URL = "postgresql://azureuser:azure@localhost:5432/predictions"

engine = create_engine(DATABASE_URL, echo=True) 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Prediction(Base):
    __tablename__ = "predictions" 
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    predictions = relationship("Prediction", back_populates="user") 

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    input_data = Column(String, nullable=False)
    prediction = Column(Float, nullable=False)
    actual_result = Column(Float, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="predictions")
        
def init_db():
    Base.metadata.create_all(bind=engine)
def register_user(username, email, password):
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            raise ValueError("User with this username or email already exists.")
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.add(new_user)
        db.commit()
        return new_user
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def authenticate_user(username, password):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user and user.check_password(password):
            return user
        return None
    finally:
        db.close()


def save_prediction(input_data, prediction):
    db = SessionLocal()
    try:
        if isinstance(input_data, list):
            input_data = {
                "team1": input_data[0][0],
                "team2": input_data[0][1],
                "season": input_data[0][2]
            }

        new_prediction = Prediction(input_data=str(input_data), prediction=float(prediction))
        db.add(new_prediction)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_user_predictions(user_id):
    db = SessionLocal()
    try:
        return db.query(Prediction).filter(Prediction.user_id == user_id).all()
    finally:
        db.close()
Base = declarative_base()
