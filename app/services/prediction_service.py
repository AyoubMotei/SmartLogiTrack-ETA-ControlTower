import joblib
import pandas as pd
import os
import sys
from sqlalchemy.orm import Session
from app.models import ETAPrediction
from app.schemas import TripFeatures

class PredictionService:
    def __init__(self):
        # Construction dynamique du chemin absolu vers le modèle
        # app/services/prediction_service.py -> app/services -> app -> root -> models/model_eta.pkl
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(current_dir, "../../models/model_eta.pkl")
        self.model_path = os.path.normpath(self.model_path)
        
        self.model = None
        self.load_model()

    def load_model(self):
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                print(f"Modèle chargé avec succès : {self.model_path}")
            except Exception as e:
                print(f"Erreur critique : Impossible de charger le modèle à {self.model_path}. Erreur : {e}")
        else:
            print(f"Fichier modèle introuvable : {self.model_path}")

    def predict(self, features: TripFeatures, db: Session) -> float:
        """
        Effectue une prédiction et l'enregistre en base.
        Si l'enregistrement échoue, la prédiction est quand même retournée.
        """
        if self.model is None:
            # Tentative de rechargement à chaud (optionnel mais utile)
            self.load_model()
            if self.model is None:
                raise Exception("Modèle ETA non disponible (fichier manquant ou corrompu).")

        # 1. Préparation des données pour le modèle
        # Conversion du schéma Pydantic en DataFrame (attendu par sklearn)
        data = pd.DataFrame([features.dict()])

        try:
            # 2. Inférence
            prediction = self.model.predict(data)[0]
            prediction_value = float(prediction)
        except Exception as e:
            raise Exception(f"Erreur lors de l'inférence du modèle : {e}")

        # 3. Monitoring / Logging en base de données
        try:
            db_prediction = ETAPrediction(
                trip_distance=features.trip_distance,
                pickup_hour=features.pickup_hour,
                day_of_week=features.day_of_week,
                month=features.month,
                estimated_duration=prediction_value,
                model_version="1.0.0"
                # timestamp est géré par défaut dans models.py
            )
            db.add(db_prediction)
            db.commit()
            db.refresh(db_prediction)
            print(f"Prédiction enregistrée ID: {db_prediction.id}")
        except Exception as e:
            # Résilience : on ne bloque pas la réponse si le log échoue
            db.rollback()
            print(f"ALERTE MONITORING : Échec de l'enregistrement en base. Erreur : {e}", file=sys.stderr)

        return prediction_value

# Instanciation unique du service pour importation dans main.py
prediction_service = PredictionService()
