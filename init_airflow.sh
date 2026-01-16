#!/bin/bash
# init_airflow.sh

# Initialiser la base de données interne d'Airflow
airflow db init

# Créer compte utilisateur Admin
airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com