import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
import joblib
import os
from config import COMMISSION_RATE
from database import get_employee_sale_count

MODEL_PATH = "rf_model.joblib"
CLUSTER_MODEL_PATH = "kmeans_model.joblib"

def calculate_commission(amount, employee_id):
    sale_count = get_employee_sale_count(employee_id)
    rate = COMMISSION_RATE
    if sale_count < 5:  # Bonus +5% for the first 5 sales
        rate += 0.05
    return amount * rate

def prepare_features(df):
    try:
        if df.empty:
            return None, None, "DataFrame is empty"
        
        df["sale_date"] = pd.to_datetime(df["sale_date"])
        df["days"] = (df["sale_date"] - df["sale_date"].min()).dt.days
        df["day_of_week"] = df["sale_date"].dt.dayofweek
        
        employee_stats = df.groupby("name").agg({
            "amount": ["count", "mean", "sum"],
            "commission": "sum",
            "days": "max"
        }).reset_index()
        employee_stats.columns = ["name", "sale_count", "avg_sale_amount", "total_sales", "total_commission", "max_days"]
        
        features = df[["days", "amount", "day_of_week"]].copy()
        features["sale_count"] = df.groupby("name")["amount"].transform("count")
        features["avg_sale_amount"] = df.groupby("name")["amount"].transform("mean")
        
        return features, employee_stats, None
    except Exception as e:
        return None, None, f"Feature preparation error: {e}"

def train_and_predict(df):
    try:
        print("Starting train_and_predict")
        features, employee_stats, error = prepare_features(df)
        if error:
            print(f"Error in prepare_features: {error}")
            return None, None, None, [], error
        
        X = features[["days", "amount", "day_of_week", "sale_count", "avg_sale_amount"]]
        y = df["commission"]
        
        if len(X) < 2:
            print("Not enough data to train the model")
            return None, None, None, [], "Not enough data to train the model"
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        joblib.dump(model, MODEL_PATH)
        print(f"Model saved to {MODEL_PATH}")
        
        future_X = X.iloc[-1:].copy()
        future_X["days"] += 30
        predicted_commission = model.predict(future_X)[0]
        
        cluster_features = employee_stats[["sale_count", "avg_sale_amount", "total_commission"]]
        n_clusters = min(3, len(cluster_features))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        employee_stats["cluster"] = kmeans.fit_predict(cluster_features)
        joblib.dump(kmeans, CLUSTER_MODEL_PATH)
        print(f"Cluster model saved to {CLUSTER_MODEL_PATH}")
        
        recommendations = []
        for name, row in employee_stats.iterrows():
            if row["cluster"] == employee_stats["cluster"].max():
                recommendations.append(f"{name}: Increase sales frequency or average deal amount.")
            else:
                recommendations.append(f"{name}: Keep up the good work!")
        
        print("train_and_predict completed successfully")
        return model, predicted_commission, employee_stats, recommendations, None
    except Exception as e:
        print(f"Error in train_and_predict: {e}")
        return None, None, None, [], f"Model training error: {e}"

def analyze_sales(df):
    try:
        print("Starting analyze_sales")
        if df.empty:
            print("DataFrame is empty, analysis impossible")
            return None, None, None, None, "DataFrame is empty"
        
        total_sales = df["amount"].sum()
        total_commissions = df["commission"].sum()
        avg_commission = df["commission"].mean()
        
        features, employee_stats, error = prepare_features(df)
        if error:
            print(f"Error in prepare_features: {error}")
            return total_sales, total_commissions, avg_commission, None, error
        
        X = features[["days", "amount", "day_of_week", "sale_count", "avg_sale_amount"]]
        y = df["commission"]
        
        model = None
        predicted_commission = 0
        recommendations = []
        
        if os.path.exists(MODEL_PATH):
            print(f"Loading saved model from {MODEL_PATH}")
            try:
                model = joblib.load(MODEL_PATH)
                future_X = X.iloc[-1:].copy()
                future_X["days"] += 30
                predicted_commission = model.predict(future_X)[0]
                
                if os.path.exists(CLUSTER_MODEL_PATH):
                    print(f"Loading cluster model from {CLUSTER_MODEL_PATH}")
                    kmeans = joblib.load(CLUSTER_MODEL_PATH)
                    cluster_features = employee_stats[["sale_count", "avg_sale_amount", "total_commission"]]
                    employee_stats["cluster"] = kmeans.predict(cluster_features)
                    for name, row in employee_stats.iterrows():
                        if row["cluster"] == employee_stats["cluster"].max():
                            recommendations.append(f"{name}: Increase sales frequency or average deal amount.")
                        else:
                            recommendations.append(f"{name}: Keep up the good work!")
            except Exception as e:
                print(f"Model loading error: {e}")
                model, predicted_commission, employee_stats, recommendations, error = train_and_predict(df)
                if error:
                    print(f"Error after retraining: {error}")
                    return total_sales, total_commissions, avg_commission, None, error
        else:
            print("Saved model not found, training new model")
            model, predicted_commission, employee_stats, recommendations, error = train_and_predict(df)
            if error:
                print(f"Error training new model: {error}")
                return total_sales, total_commissions, avg_commission, None, error
        
        print("analyze_sales completed successfully")
        return (total_sales, total_commissions, avg_commission,
                (model, X, y, X.iloc[-1:].copy(), predicted_commission, employee_stats, recommendations), None)
    except Exception as e:
        print(f"Error in analyze_sales: {e}")
        return None, None, None, None, f"Analysis error: {e}"