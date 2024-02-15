import datetime as dt
import json

import requests
from flask import Flask, jsonify, request

API_TOKEN = <YOUR_API_TOKEN>

#https://www.visualcrossing.com
WEATHER_KEY = "YUOR_WEATHER_API"
#https://api-ninjas.com
INFO_KEY = "YOUR_NINJAS_API"

app = Flask(__name__)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv

def get_weather(location, date1):
    url_base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
    date2 = '-' # optional (по можливості)
    unit_group = 'metric'   
    url = f"{url_base_url}/{location}/{date1}?key={WEATHER_KEY}&unitGroup={unit_group}"
    response = requests.get(url)
    data = response.json()
    weather_data = data['days'][0]
    return weather_data

def get_info(location):
    name = location.split(',')[0]
    api_url = 'https://api.api-ninjas.com/v1/city?name={}'.format(name)
    response = requests.get(api_url, headers={'X-Api-Key': INFO_KEY})
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        print("Error:", response.status_code, response.text)

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>KMA L2: python Saas.</h2></p>"


@app.route(<YOUR_ROUTE>, methods=["POST"])
def weather_endpoint():
    json_data = request.get_json()

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)
    token = json_data.get("token")
    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)
    exclude = ""
    if json_data.get("exclude"):
        exclude = json_data.get("exclude")
        
    # data from request
    requester_name = json_data.get("requester_name")
    location = json_data.get("location")
    date = json_data.get("date")
    
    # data from weather site
    weather_data = get_weather(location, date)
    
    # location info:

    location_info = get_info(location)
    
    result = {
        "requester_name": requester_name,
        "location": location,
        "date": date,
        "weather":
        {
            "temp_c": weather_data['temp'],
            "feelslike": weather_data['feelslike'],
            "wind_kph": weather_data['windspeed'],
            "humidity": weather_data['humidity'],
            "snow": weather_data['snow'],
            "sunrise": weather_data['sunrise'],
            "sunset": weather_data['sunset'],
            "cloudcover": weather_data['cloudcover'],
            "precipitation": weather_data['precip']
        },
        "location_info": location_info[0]   # to get rid of list
    }
    return result
