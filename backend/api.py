from fastapi import FastAPI
import pickle
import numpy as np

app = FastAPI()

model = pickle.load(open("ml_model/model.pkl","rb"))

@app.post("/predict")

def predict(data: dict):

    features = np.array([
        data["weekend"],
        data["rain"],
        data["temperature"],
        data["previous_sales"]
    ]).reshape(1,-1)

    prediction = model.predict(features)

    return {"prediction": int(prediction[0])}