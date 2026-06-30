import datetime
import os

# --- AZURE / OpenAI configuration (loaded from environment variables)
# Set these in your environment to avoid committing secrets.
# Example (PowerShell): $env:AZURE_OPENAI_KEY = 'sk-...'
AZURE_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "https://healthcareassistant.openai.azure.com/")
AZURE_KEY = os.environ.get("AZURE_OPENAI_KEY", "")
AZURE_MODEL = os.environ.get("AZURE_OPENAI_MODEL", "gpt-4o")
AZURE_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01")

# File Path
USERS_FILE = "users.csv"
DISEASE_FILE = "disease_reports_v2.csv"
PROFILES_FILE = "user_profiles.csv"

# --- Url link ---
LOTTIE_HEALTH_URL = "https://lottie.host/9c339797-4011-4475-a044-6a9cb57b7f43/4WnLqV9x6F.json"
LOTTIE_AI_URL = "https://lottie.host/575a7bc0-2183-4318-9d41-3945a6396b99/jQ8P9xW2x2.json"

# --- Disease LISTS ---
DISEASE_OPTIONS = [
    "Dengue", "Malaria", "Covid-19", "Flu (Influenza)", "Typhoid",
    "Chikungunya", "Common Cold", "Food Poisoning", "Migraine",
    "Chickenpox", "Conjunctivitis (Pink Eye)", "Allergies",
    "Gastroenteritis", "Pneumonia", "Tuberculosis"
]

CITY_COORDINATES = {
    "New Delhi": (28.6139, 77.2090), "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777), "Bangalore": (12.9716, 77.5946),
    "Chennai": (13.0827, 80.2707), "Kolkata": (22.5726, 88.3639),
    "Hyderabad": (17.3850, 78.4867), "Ahmedabad": (23.0225, 72.5714),
    "Pune": (18.5204, 73.8567), "Jaipur": (26.9124, 75.7873),
    "Lucknow": (26.8467, 80.9462), "Kanpur": (26.4499, 80.3319),
    "Nagpur": (21.1458, 79.0882), "Indore": (22.7196, 75.8577),
    "Patna": (25.5941, 85.1376), "Bhopal": (23.2599, 77.4126),
    "Visakhapatnam": (17.6868, 83.2185), "Vadodara": (22.3072, 73.1812),
    "Ludhiana": (30.9010, 75.8573), "Agra": (27.1767, 78.0081),
    "Nashik": (19.9975, 73.7898), "Guwahati": (26.1445, 91.7362),
    "Chandigarh": (30.7333, 76.7794), "Thiruvananthapuram": (8.5241, 76.9366),
    "Bhubaneswar": (20.2961, 85.8245), "Raipur": (21.2514, 81.6296)
}
