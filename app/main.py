from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
import os

# Imports absolus stricts
from app import models, schemas, auth
from app.database import engine, get_db
from app.services.prediction_service import prediction_service
from app.services.analytics_service import analytics_service

# Tentative de création des tables au démarrage avec gestion d'erreurs
try:
    models.Base.metadata.create_all(bind=engine)
    print("Tables de base de données vérifiées/créées avec succès.")
except Exception as e:
    print(f"Erreur critique au démarrage (Base de données) : {e}")

app = FastAPI(
    title="SmartLogiTrack ETA Control Tower",
    description="API de production pour la prédiction d'ETA et l'analyse logistique.",
    # version="1.0.0"
)

# --- Authentification ---

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Authentification simulée (Admin par défaut)
    if form_data.username != "admin" or form_data.password != "admin123":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Création du token JWT
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Endpoint Prédiction (Sécurisé & Monitoré) ---

@app.post("/predict", response_model=schemas.PredictionResponse)
async def predict_eta(
    features: schemas.TripFeatures,
    current_user: schemas.TokenData = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Appel du service qui gère la prédiction ET le logging en base
        eta = prediction_service.predict(features, db)
        return {
            "estimated_duration": eta,
            
        }
    except Exception as e:
        # Erreur 500 générique en cas de plantage du modèle (DB errors sont gérées dans le service)
        raise HTTPException(status_code=500, detail=str(e))

# --- Endpoints Analytics (Sécurisés & SQL Pur) ---

@app.get("/analytics/avg-duration-by-hour", response_model=List[schemas.AvgDurationByHour])
async def get_avg_duration_by_hour(
    current_user: schemas.TokenData = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return analytics_service.get_avg_duration_by_hour(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne Analytics : {str(e)}")

@app.get("/analytics/payment-analysis", response_model=List[schemas.PaymentAnalysis])
async def get_payment_analysis(
    current_user: schemas.TokenData = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return analytics_service.get_payment_analysis(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne Analytics : {str(e)}")

# --- Root ---

@app.get("/")
def read_root():
    return {"message": "SmartLogiTrack API is Running"}
