# Attempt import for Azure/OpenAI
try:
    from openai import AzureOpenAI, OpenAI
except ImportError:
    AzureOpenAI = None
    OpenAI = None

from .config import AZURE_ENDPOINT, AZURE_KEY, AZURE_MODEL, AZURE_API_VERSION
import streamlit as st


def get_ai_client():
    if not AZURE_KEY or AZURE_KEY.startswith("<REDACTED>"): return None
    try:
        if AzureOpenAI and "azure" in AZURE_ENDPOINT:
            return AzureOpenAI(api_version=AZURE_API_VERSION, azure_endpoint=AZURE_ENDPOINT, api_key=AZURE_KEY)
        elif OpenAI:
            return OpenAI(base_url=AZURE_ENDPOINT, api_key=AZURE_KEY)
    except Exception:
        return None

def generate_daily_briefing(weather_data, nearby_df, user_profile):
    client = get_ai_client()
    if not client: return "AI Configuration Missing."

    disease_context = "No outbreaks."
    if nearby_df is not None and not nearby_df.empty:
        counts = nearby_df['disease'].value_counts().to_string()
        disease_context = f"Outbreaks nearby:{counts}"

    weather_context = f"Temp: {weather_data['temp']}C" if weather_data else "No weather data."
    profile_context = user_profile if user_profile else "None."

    system_prompt = "You are a Medical Intelligence System. Provide a concise 'Daily Health Briefing' (Risk, Threat, Action Plan)."
    user_prompt = f"Profile: {profile_context} Weather: {weather_context} Diseases: {disease_context}"

    try:
        completion = client.chat.completions.create(
            model=AZURE_MODEL, messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], max_tokens=300
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"AI Error: {e}"


def generate_trend_analysis(daily_counts_dict):
    client = get_ai_client()
    if not client: return "AI Missing."
    if not daily_counts_dict: return "Not enough data."
    data_str = "".join([f"{k}: {v}" for k, v in daily_counts_dict.items()])
    system_prompt = "You are an Epidemiologist. Analyze the daily case counts. 1. Trend 2. Prediction 3. Recommendation. Max 50 words."
    try:
        completion = client.chat.completions.create(
            model=AZURE_MODEL, messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Data: {data_str}"}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"AI Error: {e}"


def generate_ai_response(user_input, risk_level, data_db):
    client = get_ai_client()
    if not client: return "AI Offline."
    profile = data_db.get_user_profile(st.session_state.get('username'))
    context = f"Profile: {profile} Risk Level: {risk_level}"
    try:
        completion = client.chat.completions.create(
            model=AZURE_MODEL,
            messages=[{"role": "system", "content": f"You are Vita AI. Context: {context}. Disclaimer: See a doctor."}, {"role": "user", "content": user_input}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"AI Error: {e}"
