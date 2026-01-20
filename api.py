from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import requests
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

model = joblib.load("priority_model.pkl")

class InputData(BaseModel):
    damage_score: float
    population: int
    hospitals: int
    roads: int

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # hackathon safe
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/predict")
def predict(data: InputData):
    features = [[
        data.damage_score,
        data.population,
        data.hospitals,
        data.roads
    ]]
    prediction = model.predict(features)[0]
    return {"priority": prediction}

 


OPENWEATHER_KEY = "b87ab21875ce2a31a12a304b0f8ea571"

@app.get("/live-alerts")
def live_alerts(lat: float, lon: float):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}"
    )

    resp = requests.get(url)
    data = resp.json()
    print(data)

    # OpenWeather does NOT always give alerts
    # So we infer risk from weather conditions
    weather = data.get("weather", [])

    if not weather:
        return {"status": "unknown", "message": "No weather data"}

    condition = weather[0]["main"]

    if condition in ["Rain", "Thunderstorm", "Snow"]:
        return {
            "status": "alert",
            "type": condition,
            "message": f"Potential {condition.lower()} risk detected"
        }

    return {
        "status": "safe",
        "message": "No immediate disaster risk detected"
    }
