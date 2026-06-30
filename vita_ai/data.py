import os
import datetime
import pandas as pd
from .config import DISEASE_FILE, PROFILES_FILE
from .utils import calculate_distance


class DataManager:
    def __init__(self):
        self.csv_file = DISEASE_FILE
        self.profiles_file = PROFILES_FILE
        if not os.path.exists(self.csv_file): self.init_csv()
        if not os.path.exists(self.profiles_file): self.init_profiles_db()

    def init_csv(self):
        pd.DataFrame(columns=["lat", "lng", "disease", "weight", "user_id", "timestamp"]).to_csv(self.csv_file, index=False)

    def init_profiles_db(self):
        pd.DataFrame(columns=["username", "medical_history", "last_updated"]).to_csv(self.profiles_file, index=False)

    def get_user_profile(self, username):
        try:
            df = pd.read_csv(self.profiles_file)
            user_data = df[df["username"] == username]
            if not user_data.empty: return user_data.iloc[0]["medical_history"]
        except Exception:
            return None
        return None

    def update_user_profile(self, username, history_text):
        new_row = {"username": username, "medical_history": history_text, "last_updated": datetime.datetime.now()}
        try:
            if os.path.exists(self.profiles_file):
                df = pd.read_csv(self.profiles_file)
                if "username" not in df.columns: df["username"] = ""
                if username in df["username"].astype(str).values:
                    df.loc[df["username"].astype(str) == username, "medical_history"] = history_text
                    df.loc[df["username"].astype(str) == username, "last_updated"] = datetime.datetime.now()
                else:
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            else:
                df = pd.DataFrame([new_row])
            df.to_csv(self.profiles_file, index=False)
            return True
        except Exception:
            return False

    def add_report(self, lat, lng, disease, weight, user_id):
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_data = pd.DataFrame([{ 
            "lat": float(lat), "lng": float(lng), "disease": str(disease),
            "weight": int(weight), "user_id": str(user_id), "timestamp": ts
        }])
        try:
            header = not os.path.exists(self.csv_file)
            with open(self.csv_file, "a", newline="", encoding="utf-8") as f:
                new_data.to_csv(f, mode="a", header=header, index=False)
                f.flush()
                try: os.fsync(f.fileno())
                except: pass
            return True, "Report submitted."
        except PermissionError:
            return False, "❌ Error: File is open elsewhere."
        except Exception as e:
            return False, f"Error: {e}"

    def get_data(self, user_filter=None):
        if not os.path.exists(self.csv_file): return pd.DataFrame()
        try:
            df = pd.read_csv(self.csv_file)
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
                df.loc[df["timestamp"].isna(), "timestamp"] = datetime.datetime.now()
            if "lat" in df.columns and "lng" in df.columns:
                df["lat"] = pd.to_numeric(df["lat"], errors='coerce')
                df["lng"] = pd.to_numeric(df["lng"], errors='coerce')
                df = df.dropna(subset=["lat", "lng"])
            if "weight" in df.columns:
                df["weight"] = pd.to_numeric(df["weight"], errors='coerce').fillna(1)
            if user_filter:
                return df[df["user_id"] == user_filter]
            return df
        except Exception:
            return pd.DataFrame()

    def get_filtered_data(self, user_lat, user_lng, radius_km, mode, lookback_days=30, selected_year=None, selected_month=None):
        df = self.get_data()
        if df.empty: return pd.DataFrame(), 0, "Unknown", pd.DataFrame()

        if mode == "Historical Archive" and selected_year and selected_month:
            df_filtered = df[(df['timestamp'].dt.year == selected_year) & (df['timestamp'].dt.month == selected_month)].copy()
        else:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=lookback_days)
            df_filtered = df[df["timestamp"] >= cutoff_date].copy()

        if df_filtered.empty: return pd.DataFrame(), 0, "Safe", df_filtered

        df_filtered["distance_km"] = df_filtered.apply(lambda row: calculate_distance(user_lat, user_lng, row["lat"], row["lng"]), axis=1)
        nearby_cases = df_filtered[df_filtered["distance_km"] <= radius_km].copy()

        total_risk = nearby_cases["weight"].sum()
        risk_level = "Safe"
        if total_risk > 0: risk_level = "Moderate"
        if total_risk > 15: risk_level = "High"

        return nearby_cases, round(total_risk, 1), risk_level, df_filtered
