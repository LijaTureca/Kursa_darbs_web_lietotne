#database.py
import numpy as np
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

# PostgreSQL
DATABASE_URL = "postgresql://azureuser:azure@52.233.181.73:5432/predictions"
#DATABASE_URL = "postgresql://azureuser:azure@localhost:5432/predictions"

engine = create_engine(DATABASE_URL, echo=True) 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Prediction(Base):
    __tablename__ = "predictions" 

    id = Column(Integer, primary_key=True, index=True)  
    date = Column(DateTime, default=datetime.datetime.utcnow)  
    input_data = Column(String, nullable=False)  
    prediction = Column(Float, nullable=False)  
    actual_result = Column(Float, nullable=True) 

def init_db():
    Base.metadata.create_all(bind=engine)


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


def get_all_predictions():
    db = SessionLocal()
    try:
        predictions = db.query(Prediction).all()
        return predictions
    finally:
        db.close()

Base = declarative_base()
