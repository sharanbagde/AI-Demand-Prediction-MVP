import streamlit as st
import pandas as pd
import pickle
import streamlit as st


# Load trained model
with open("demand_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("label_encoder.pkl", "rb") as f:
    le = pickle.load(f)

st.set_page_config(
    page_title="Local Cafe Demand Predictor",
    layout="centered"
)

st.title("☕ Local Café Demand Prediction System")
st.subheader("Predict Tomorrow's Demand (Low / Medium / High)")
st.markdown("### 📈 Model Performance")
st.info("Model Accuracy: **82.34%** (evaluated on test data)")
st.markdown("---")


# Input Form
with st.form("prediction_form"):
    col1, col2 = st.columns(2)

    with col1:
        is_weekend = st.selectbox(
            "Is Tomorrow a Weekend?",
            [0, 1],
            format_func=lambda x: "Yes" if x == 1 else "No"
        )

        avg_temp = st.slider(
            "Average Temperature (°C)",
            20, 45, 32
        )

        festival_index = st.selectbox(
            "Festival Impact Level",
            [
                ("No Festival", 0.0),
                ("Minor Festival", 1.2),
                ("Medium Festival", 1.5),
                ("Major Festival", 1.8)
            ],
            format_func=lambda x: x[0]
        )[1]

    with col2:
        is_rainy = st.selectbox(
            "Is it a Rainy Day?",
            [0, 1],
            format_func=lambda x: "Yes" if x == 1 else "No"
        )

        prev_sales = st.number_input(
            "Previous Day Sales",
            min_value=50,
            max_value=300,
            value=120
        )

    submit = st.form_submit_button("Predict Demand")

# Prediction
if submit:
    input_df = pd.DataFrame([{
        "is_weekend": is_weekend,
        "avg_temp_c": avg_temp,
        "is_rainy": is_rainy,
        "festival_index": festival_index,
        "previous_day_sales": prev_sales
    }])

    prediction = model.predict(input_df)
    result = le.inverse_transform(prediction)[0]

    st.markdown("---")
    st.subheader("📊 Prediction Result")

    if result == "High":
        st.success("🔥 High Demand Expected Tomorrow")
    elif result == "Medium":
        st.warning("⚖️ Medium Demand Expected Tomorrow")
    else:
        st.error("📉 Low Demand Expected Tomorrow")

    st.info(f"Predicted Demand Category: **{result}**")
