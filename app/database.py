from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupération de l'URL de base de données
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Valeur par défaut pour le développement local si .env absent
    DATABASE_URL = "postgresql://postgres:123@127.0.0.1:5432/smartlogi_db"

# Création de l'engine avec encodage UTF-8 forcé pour Windows
engine = create_engine(
    DATABASE_URL,
    connect_args={"client_encoding": "utf8"}
)

# Session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles SQLAlchemy
Base = declarative_base()

# Dépendance pour obtenir la session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
