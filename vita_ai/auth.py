import os
import hashlib
import pandas as pd
from .config import USERS_FILE


class AuthManager:
    def __init__(self):
        self.users_file = USERS_FILE
        if not os.path.exists(self.users_file):
            pd.DataFrame(columns=["username", "password_hash", "age", "gender"]).to_csv(self.users_file, index=False)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def signup(self, username, password, age=None, gender=None):
        try:
            df = pd.read_csv(self.users_file)
            if username in df["username"].values:
                return False, "Username already exists."
            new_user = pd.DataFrame([{"username": username, "password_hash": self.hash_password(password), "age": age, "gender": gender}])
            new_user.to_csv(self.users_file, mode="a", header=False, index=False)
            return True, "Account created! Please login."
        except Exception as e:
            return False, f"Error: {e}"

    def login(self, username, password):
        try:
            df = pd.read_csv(self.users_file)
            user_row = df[df["username"] == username]
            if not user_row.empty:
                if user_row.iloc[0]["password_hash"] == self.hash_password(password):
                    return True
        except Exception:
            pass
        return False

    def get_user_info(self, username):
        try:
            df = pd.read_csv(self.users_file)
            user_row = df[df["username"] == username]
            if not user_row.empty:
                row = user_row.iloc[0]
                return {"age": int(row.get("age")) if not pd.isna(row.get("age")) else None,
                        "gender": row.get("gender") if not pd.isna(row.get("gender")) else None}
        except Exception:
            pass
        return {"age": None, "gender": None}

    def update_user_info(self, username, age=None, gender=None):
        try:
            df = pd.read_csv(self.users_file)
            if username in df["username"].values:
                if age is not None: df.loc[df["username"] == username, "age"] = age
                if gender is not None: df.loc[df["username"] == username, "gender"] = gender
                df.to_csv(self.users_file, index=False)
                return True
            return False
        except Exception:
            return False
