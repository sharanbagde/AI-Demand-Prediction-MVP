import streamlit as st
import pandas as pd
import pickle
import plotly.express as px
import datetime

from utils.weather_api import get_weather
from database.firebase_db import save_prediction, db

# Load model
with open("ml_model/demand_model.pkl", "rb") as f:
    model = pickle.load(f)

st.set_page_config(page_title="Smart Demand Predictor", layout="centered")

st.title("📊 AI Demand Prediction Dashboard")

st.markdown("---")

# -----------------------------
# 📁 CSV Upload Section
# -----------------------------
st.markdown("### 📁 Upload Your Sales Data")

uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

df = None

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.success("✅ File uploaded successfully!")

    st.subheader("📄 Data Preview")
    st.dataframe(df.head())

# -----------------------------
# 📊 Chart Section
# -----------------------------
if df is not None and "daily_demand" in df.columns:

    st.markdown("---")
    st.subheader("📈 Demand Trend (Your Data)")

    fig = px.line(
        df,
        y="daily_demand",
        title="Demand Over Time",
        markers=True
    )

    st.plotly_chart(fig)

# -----------------------------
# 🏪 Manual Prediction Section
# -----------------------------
st.markdown("---")
st.markdown("### 🏪 Manual Prediction")

business_type = st.selectbox(
    "Business Type",
    ["Cafe", "Bakery", "Restaurant", "Juice Shop", "Grocery Store"]
)

city = st.text_input("City / Location", "Nagpur")

# Festival
festival_name = st.selectbox(
    "Festival",
    ["None", "Holi", "Eid", "Diwali", "Christmas"]
)

festival_mapping = {
    "None": 0.0,
    "Holi": 1.2,
    "Eid": 1.5,
    "Diwali": 1.8,
    "Christmas": 1.5
}

festival_index = festival_mapping[festival_name]

# Form
with st.form("prediction_form"):

    col1, col2 = st.columns(2)

    with col1:
        is_weekend = st.selectbox(
            "Is Tomorrow a Weekend?",
            [0, 1],
            format_func=lambda x: "Yes" if x == 1 else "No"
        )

    with col2:
        prev_sales = st.number_input(
            "Previous Day Sales",
            min_value=50,
            max_value=1000,
            value=120
        )

    day_of_week = st.selectbox(
        "Day of Week",
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    )

    submit = st.form_submit_button("Predict Demand")

# Mapping
day_mapping = {
    "Monday": 0, "Tuesday": 1, "Wednesday": 2,
    "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6
}

# -----------------------------
# 🔮 Manual Prediction Logic
# -----------------------------
if submit:

    weather = get_weather(city)

    if weather is None:
        st.error("❌ Could not fetch weather data.")
    else:
        avg_temp, rainfall, is_rainy = weather

        st.markdown("---")
        st.subheader("🌦 Weather Data")

        st.info(f"🌡 Temperature: {avg_temp:.1f} °C")
        st.info(f"🌧 Rainfall: {rainfall:.1f} mm")

        input_df = pd.DataFrame([{
            "day_of_week": day_mapping[day_of_week],
            "is_weekend": is_weekend,
            "avg_temp_c": avg_temp,
            "rainfall_mm": rainfall,
            "is_rainy": is_rainy,
            "festival_index": festival_index,
            "previous_day_sales": prev_sales
        }])

        prediction = model.predict(input_df)[0]

        st.markdown("---")
        st.subheader("📊 Prediction Result")

        st.success(f"📈 Expected Demand: {int(prediction)} units")

        # Insights
        if prediction > 200:
            st.warning("⚠️ High demand expected! Prepare extra stock.")
        elif prediction > 120:
            st.info("🙂 Moderate demand expected.")
        else:
            st.error("📉 Low demand expected.")

        # Save to Firebase
        data = {
            "business_type": business_type,
            "city": city,
            "prediction": int(prediction),
            "timestamp": datetime.datetime.now().isoformat()
        }

        save_prediction(data)

# -----------------------------
# 🤖 CSV Prediction Logic
# -----------------------------
if df is not None:

    try:
        last_row = df.iloc[-1]

        input_df = pd.DataFrame([{
            "day_of_week": last_row["day_of_week"],
            "is_weekend": last_row["is_weekend"],
            "avg_temp_c": last_row["avg_temp_c"],
            "rainfall_mm": last_row["rainfall_mm"],
            "is_rainy": last_row["is_rainy"],
            "festival_index": last_row["festival_index"],
            "previous_day_sales": last_row["previous_day_sales"]
        }])

        prediction = model.predict(input_df)[0]

        st.markdown("---")
        st.subheader("🤖 Prediction from Your Uploaded Data")

        st.success(f"Next Day Demand: {int(prediction)} units")

        # Save to Firebase
        data = {
            "business_type": "CSV Upload",
            "city": "N/A",
            "prediction": int(prediction),
            "timestamp": datetime.datetime.now().isoformat()
        }

        save_prediction(data)

    except Exception:
        st.error("⚠️ CSV format issue. Please check column names.")

# -----------------------------
# 📜 Prediction History
# -----------------------------
st.markdown("---")
st.subheader("📜 Prediction History")

docs = db.collection("predictions").stream()

history = []

for doc in docs:
    history.append(doc.to_dict())

if history:
    df_history = pd.DataFrame(history)
    st.dataframe(df_history)
else:
    st.info("No history available yet.")