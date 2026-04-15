import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
import joblib
import os
import datetime

# Handle config path depending on where it's executed from
try:
    from config import Config
except ImportError:
    class Config:
        MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')

class ProductivityModel:
    def __init__(self):
        self.models_dir = Config.MODELS_DIR
        os.makedirs(self.models_dir, exist_ok=True)
        
        self.regression_path = os.path.join(self.models_dir, 'time_predictor.pkl')
        self.classifier_path = os.path.join(self.models_dir, 'procrastination_detector.pkl')
        self.cluster_path = os.path.join(self.models_dir, 'peak_hours_cluster.pkl')
        
        self.regressor = None
        self.classifier = None
        self.clusterer = None
        
        self._load_or_init_models()

    def _load_or_init_models(self):
        """Load existing trained models, or initialize new ones if none exist."""
        try:
            if os.path.exists(self.regression_path):
                self.regressor = joblib.load(self.regression_path)
            else:
                self.regressor = LinearRegression()

            if os.path.exists(self.classifier_path):
                self.classifier = joblib.load(self.classifier_path)
            else:
                self.classifier = RandomForestClassifier(n_estimators=10, random_state=42)

            if os.path.exists(self.cluster_path):
                self.clusterer = joblib.load(self.cluster_path)
            else:
                self.clusterer = KMeans(n_clusters=3, random_state=42, n_init=10)
        except Exception as e:
            print(f"Error loading models: {e}")
            self.regressor = LinearRegression()
            self.classifier = RandomForestClassifier(n_estimators=10, random_state=42)
            self.clusterer = KMeans(n_clusters=3, random_state=42, n_init=10)

    def train_initial_models_with_synthetic_data(self):
        """
        Creates synthetic data to overcome the cold-start problem.
        Trains all three ML models and saves them to disk.
        """
        # 1. Regression Data: Predict actual_time based on estimated_time and priority
        df_reg = pd.DataFrame({
            'estimated_time': np.random.randint(15, 120, 200),
            'priority': np.random.randint(1, 4, 200), # 1=low, 2=med, 3=high
            'interruptions': np.random.randint(0, 5, 200),
        })
        # Generate true labels: actual time is roughly estimated + interruption penalties + noise
        df_reg['actual_time'] = df_reg['estimated_time'] * (1 + 0.15 * df_reg['interruptions']) + np.random.normal(0, 5, 200)
        
        self.regressor.fit(df_reg[['estimated_time', 'priority', 'interruptions']], df_reg['actual_time'])
        joblib.dump(self.regressor, self.regression_path)

        # 2. Classification Data: Procrastination Risk (1=Delay, 0=On-time)
        df_clf = pd.DataFrame({
            'time_of_day': np.random.randint(8, 22, 200),
            'priority': np.random.randint(1, 4, 200),
            'past_delay_minutes': np.random.randint(0, 60, 200)
        })
        # Logic: Late hours + high past delays = high risk
        df_clf['procrastination_risk'] = ((df_clf['time_of_day'] > 17) & (df_clf['past_delay_minutes'] > 20)).astype(int)
        
        self.classifier.fit(df_clf[['time_of_day', 'priority', 'past_delay_minutes']], df_clf['procrastination_risk'])
        joblib.dump(self.classifier, self.classifier_path)

        # 3. Clustering Data: Peak Productivity Hours
        df_clust = pd.DataFrame({
            'time_of_day': np.random.randint(8, 22, 200),
            'focus_score': np.random.randint(40, 100, 200) # Out of 100
        })
        self.clusterer.fit(df_clust[['time_of_day', 'focus_score']])
        joblib.dump(self.clusterer, self.cluster_path)

    def _ensure_models_trained(self):
        try:
            self.regressor.predict([[30, 2, 0]])
        except:
            self.train_initial_models_with_synthetic_data()

    def predict_task_duration(self, estimated_time, priority_str, interruptions=0):
        """Regression Model: Predict how long a task will actually take."""
        self._ensure_models_trained()
        priority_map = {'low': 1, 'medium': 2, 'high': 3}
        p_val = priority_map.get(priority_str.lower() if isinstance(priority_str, str) else 'medium', 2)
        
        features = pd.DataFrame([[estimated_time, p_val, interruptions]], 
                                columns=['estimated_time', 'priority', 'interruptions'])
        predicted_time = self.regressor.predict(features)[0]
        return max(5, round(predicted_time)) # Ensure at least 5 mins

    def predict_procrastination_risk(self, priority_str, past_delay=0):
        """Classification Model: Returns risk of procrastination out of 100%."""
        self._ensure_models_trained()
        priority_map = {'low': 1, 'medium': 2, 'high': 3}
        p_val = priority_map.get(priority_str.lower() if isinstance(priority_str, str) else 'medium', 2)
        hour = datetime.datetime.now().hour
        
        features = pd.DataFrame([[hour, p_val, past_delay]], 
                                columns=['time_of_day', 'priority', 'past_delay_minutes'])
        risk_prob = self.classifier.predict_proba(features)[0][1] # Get prob for class 1
        return round(risk_prob * 100)
        
    def get_peak_productivity_hour(self):
        """Clustering Model: Returns the optimal hour of day for deep work."""
        self._ensure_models_trained()
        try:
            centroids = self.clusterer.cluster_centers_
            # Assuming format is [time_of_day, focus_score]
            # Find cluster with highest average focus score
            best_cluster = max(centroids, key=lambda x: x[1])
            return round(best_cluster[0])
        except Exception:
            return 10 # Default to 10 AM if clustering fails
