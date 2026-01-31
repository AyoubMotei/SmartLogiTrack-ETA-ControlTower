import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os

def train():
    print("Chargement des données...")
    # On garde l'encodage utf-16 qui a fonctionné pour ton fichier
    df = pd.read_csv('data_gold.csv', encoding='utf-16')
    
    # --- PHASE DE NETTOYAGE (Pour booster le score) ---
    # On retire les trajets aberrants (moins de 2 min, plus de 1h30)
    # et les distances de 0 km ou trop élevées (> 50km)
    initial_count = len(df)
    df = df[(df['duration_minutes'] > 2) & (df['duration_minutes'] < 90)]
    df = df[(df['trip_distance'] > 0.5) & (df['trip_distance'] < 40)]
    print(f"Nettoyage terminé : {initial_count - len(df)} lignes aberrantes supprimées.")

    # 1. Split Features/Target
    X = df[['trip_distance', 'pickup_hour', 'day_of_week', 'month']]
    y = df['duration_minutes']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 2. Entraînement
    print(f"Entraînement du Random Forest sur {len(X_train)} lignes...")
    model = RandomForestRegressor(n_estimators=100, max_depth=15, n_jobs=-1, random_state=42)
    model.fit(X_train, y_train)
    
    # 3. CALCUL DES MÉTRIQUES
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    
    print("\n" + "="*30)
    print("RÉSULTATS DU MODÈLE")
    print(f"Score R² : {r2:.3f}")
    print(f"Erreur Moyenne (MAE) : {mae:.2f} minutes")
    print("="*30 + "\n")
    
    # 4. Sauvegarde
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, 'models/model_eta.pkl')
    print("Modèle sauvegardé dans 'models/model_eta.pkl'")

if __name__ == "__main__":
    train()