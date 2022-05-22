from datetime import datetime
import pickle
from tokenize import String
import numpy as np
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
import csv
from statistics import mean
import json

# uvicorn insite_api:app --host 0.0.0.0 --port 80

app = FastAPI(title="Predicting Relative COVID Risk")

# Represents a particular wine (or datapoint)
class personal(BaseModel):
    age: float
    vax: float
    hyper_t: float
    obesity: float
    diabetes: float
    lung_d: float
    cardio_v: float
    neuro_l: float
    renal: float
    immuno_comp: float
    blood_d: float
    sex_M: float

class location(BaseModel):
    postcode: float
    venue: str
    hour: int
    day: str 

def popularTimesRisk(hour, day, where, datafile):
    
    """
    Args:
        hour: (0-23), When one will visit a location in terms of hour of the day in 24hr time
        day: (Day name), Day of the week when one will visit a location
        where: (location name), location one will attent 
        datafile: (JSON data file), containing all popular times data 

    Return: Value of risk based on the poularity of the location
    """
    try:
        UOW_popularTimes = json.load( open( datafile ) )
    except Exception as e:
        print("ERROR: Unable to open file:",datafile,'\n')
        print(e)
        return
    try:
        data = UOW_popularTimes[where]
    except Exception as e:
        print("ERROR: Unable to find location",where,"in dataset.",'\n')
        print(e)
        return
    if hour not in range(0,23):
        print("ERROR: Value",hour,"is not in range 0-23.",'\n')
        return
    allTimes = []
    for dayName in data:
        for time in data[dayName]:
            if time != 0:
                allTimes.append(int(time))
    
    locationAvg = mean(allTimes)
    try:
        now = data[day][hour]
    except Exception as e:
        print("ERROR: Unable to find busyness from day:",day,"and time",hour,"in dataset.",'\n')
        print(e)
        return

    if (now/locationAvg) > 1:
        now *= 1.1
    else:
        now *= 0.9
    
    risk = now / (locationAvg * 4)
    risk = max(0, min(1, risk))
    return risk

@app.on_event("startup")
def load_clf():
    # Load classifier from pickle file
    with open("personal_model.pkl", "rb") as file:
        global personal_model
        personal_model = pickle.load(file)
    file.close()
    with open("location_model.pkl", "rb") as file2:
        global location_model
        location_model = pickle.load(file2)
    file2.close()

@app.post("/predict/personal")
def predictPers(person: personal):
    data_point = np.array(
        [
            [
                person.age,
                person.vax,
                person.hyper_t,
                person.obesity,
                person.diabetes,
                person.lung_d,
                person.cardio_v,
                person.neuro_l,
                person.renal,
                person.immuno_comp,
                person.blood_d,
                person.sex_M
            ]
        ]
    )
    # print(data_point)
    prediction = personal_model.predict_proba(data_point).tolist()[0][1]
    
    return {"PredictionPers": round(prediction*100, 2)}   

@app.post("/predict/location")
def predictLoc(location: location):
    series = pd.read_csv('cases2.csv', header=0, index_col=0)
    values = series.values
    currentTime = 139   # This hardcode allows for a masked date to be used

    # construct an input for a new prediction
    low = currentTime
    up = low + 5
    row = values[low:up].flatten()
    print(row)
    # make a prediction
    predicted_cases = location_model.predict(np.asarray([row]))[0]
    change = predicted_cases - values[up-1]
    print(change)
    
    predicted_risk = popularTimesRisk(location.hour, location.day, location.venue, 'UOW_popularTimes.json')
    
    return {"PredictionCases": round(predicted_cases, 0), 
            "Change": round(float(change), 0),
            "PredictionRisk": round(predicted_risk*100, 2)}  