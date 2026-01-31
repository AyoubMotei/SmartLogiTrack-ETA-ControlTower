from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from app.schemas import AvgDurationByHour, PaymentAnalysis

class AnalyticsService:
    @staticmethod
    def get_avg_duration_by_hour(db: Session):
        """
        Calcule la durée moyenne des trajets par heure via une CTE SQL.
        """
        # Requête SQL brute optimisée utilisant une Common Table Expression (CTE)
        sql_query = text("""
            WITH HourlyStats AS (
                SELECT pickup_hour, AVG(duration_minutes) as mean_duration
                FROM silver_taxi_trips
                GROUP BY pickup_hour
            )
            SELECT 
                pickup_hour as pickuphour, 
                ROUND(mean_duration::numeric, 2) as avgduration
            FROM HourlyStats
            ORDER BY pickup_hour ASC;
        """)

        try:
            result = db.execute(sql_query)
            # Mapping explicite vers le schéma Pydantic
            # row[0] -> pickuphour, row[1] -> avgduration
            return [
                AvgDurationByHour(pickuphour=row[0], avgduration=row[1]) 
                for row in result
            ]
        except Exception as e:
            print(f"Erreur Analytics (Avg Duration) : {e}")
            raise e

    @staticmethod
    def get_payment_analysis(db: Session):
        """
        Analyse comparative par type de paiement.
        """
        sql_query = text("""
            SELECT 
                payment_type, 
                COUNT(*) as total_trips, 
                ROUND(AVG(duration_minutes)::numeric, 2) as avg_duration
            FROM silver_taxi_trips
            GROUP BY payment_type
            ORDER BY total_trips DESC;
        """)

        try:
            result = db.execute(sql_query)
            # Mapping vers le schéma PaymentAnalysis
            return [
                PaymentAnalysis(
                    payment_type=row[0], 
                    total_trips=row[1], 
                    avg_duration=row[2]
                ) 
                for row in result
            ]
        except Exception as e:
             print(f"Erreur Analytics (Payment Analysis) : {e}")
             raise e

# Instanciation pour usage direct
analytics_service = AnalyticsService()
