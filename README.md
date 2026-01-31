# SmartLogiTrack ETA Control Tower

Bienvenue dans la documentation technique de **SmartLogiTrack**, une tour de contrôle logistique avancée capable de prédire les temps d'arrivée (ETA) et d'analyser la performance des trajets en temps réel.

Ce projet démontre une architecture **Data Engineering & AI** complète, allant du nettoyage de données massives à leur exposition via une API sécurisée.

---

## 1. Architecture ETL (Extract, Transform, Load)

L'ingestion et le traitement des données suivent l'architecture **Medallion** (Bronze ➡️ Silver ➡️ Gold) pour garantir la qualité des données.

### 🔹 Nettoyage avec Apache Spark (Couche Silver)
Nous utilisons **PySpark** pour traiter les données brutes (Bronze) et produire une table propre (Silver) nommée `silver_taxi_trips`.

**Pourquoi Spark ?**  
Pour sa capacité à traiter des millions de lignes (Big Data) en parallèle, là où Pandas serait limité par la RAM.

**Les étapes de nettoyage clés :**
1.  **Filtrage des anomalies** : Suppression des trajets avec des durées négatives ou des distances nulles.
    ```python
    df_clean = df.filter((col("trip_distance") > 0) & (col("duration_minutes") > 0))
    ```
2.  **Standardisation des types** : Conversion des timestamps et typage strict des colonnes numériques.
3.  **Enrichissement** : Ajout de colonnes dérivées comme `day_of_week` ou `pickup_hour` pour faciliter l'analyse en aval.

---

## 2. Service de Prédiction (IA & Asynchrone)

Le cœur de l'intelligence réside dans notre modèle de Machine Learning (`model_eta.pkl`), intégré dans une API **FastAPI**.

### Integration du Modèle .pkl
Le modèle Random Forest est entraîné séparément et sérialisé avec `joblib`.

- **Chargement au démarrage** : Le modèle est chargé une seule fois en mémoire à l'instanciation de `PredictionService` pour éviter de le recharger à chaque requête .
- **Inférence** : L'API reçoit les caractéristiques du trajet (distance, heure...) et interroge le modèle.
- **Monitoring (Logging Asynchrone)** : 
    Chaque prédiction est sauvegardée en base de données (`eta_predictions`) pour surveiller la performance du modèle dans le temps (Data Drift).
    > **Note** : L'enregistrement en base est encadré par un `try/except` et un `rollback` pour s'assurer que si la base de données flanche, l'utilisateur reçoit quand même sa prédiction.

---

## 3. Sécurité (JWT - JSON Web Tokens)

L'API n'est pas ouverte à tous. Nous sécurisons l'accès aux données sensibles via le standard **OAuth2 avec JWT**.

**Le flux d'authentification :**
1.  L'utilisateur envoie `username` + `password` à l'endpoint `/token`.
2.  Le serveur vérifie les identifiants et génère un **Token signé** (chiffré avec une clé secrète `SECRET_KEY`).
3.  Ce token contient l'identité de l'utilisateur et une date d'expiration.
4.  Pour accéder à `/predict` ou `/analytics/*`, l'utilisateur doit envoyer ce token dans le header `Authorization: Bearer <token>`.

**Avantage** : Le serveur est "stateless". Il n'a pas besoin de garder une session utilisateur en mémoire ; la validité du token suffit.

---

## 4. Analytics & Performance SQL (CTEs)

Pour les tableaux de bord, la performance est critique. Nous ne faisons **aucun calcul côté Python**.

### Common Table Expressions (CTE)
Au lieu de charger 1 million de lignes dans Python pour calculer une moyenne, nous envoyons une requête SQL optimisée qui délègue le travail au moteur de base de données (PostgreSQL).

**Exemple utilisé dans `AnalyticsService` :**
```sql
WITH HourlyStats AS (
    -- Pré-agrégation des données par heure
    SELECT pickup_hour, AVG(duration_minutes) as mean_duration
    FROM silver_taxi_trips
    GROUP BY pickup_hour
)
-- Sélection finale formatée
SELECT pickup_hour, ROUND(mean_duration, 2)
FROM HourlyStats
ORDER BY pickup_hour;
```

**Pourquoi c'est mieux ?**
- **Moins de transfert réseau** : Seuls 24 lignes (pour 24h) transitent vers l'API, au lieu de millions.
- **Vitesse** : PostgreSQL est ultra-optimisé pour les agrégations (`GROUP BY`, `AVG`).

---

## Guide de Démarrage

### Pré-requis
- Python 3.10+
- PostgreSQL

### Installation
```bash
pip install -r requirements.txt
```

### Lancement du Serveur
```bash
uvicorn app.main:app --reload
```

### Tests
Lancer la suite de tests automatisés :
```bash
pytest -v
```