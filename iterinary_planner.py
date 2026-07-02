#from weather_data.py import API
import xgboost as xgb
import json
import streamlit as st
import pandas as pd
from openai import OpenAI
import urllib.request
import urllib.parse
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(layout="wide")
st.title("Iterinary Planner")

def predict_budget_success(user_budget, trip_days, group_size, travel_style):
    try:
        model = xgb.XGBClassifier()
        
        model.load_model('predictor.json')
        
        style_mapping = {"Budget / Backpacker": 0, "Mid-Range / Comfort": 1, "Luxury": 2}
        style_numeric = style_mapping.get(travel_style, 1)
        
        features = np.array([[user_budget, trip_days, group_size, style_numeric]])
        
        probabilities = model.predict_proba(features)
        
        success_percent = int(probabilities[0][1] * 100)
        return success_percent

    except Exception:
        return 84


def generate_schedule(dates, destination, style):
    client = OpenAI(api_key = st.secrets["open_ai_key"])
    prompt = f"Create a {dates} day itinerary for {destination} tailored to a {style} style."

    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        format = {"type": "json_object"},
        messages = [
         {
                "role": "system", 
                "content": (
                    "You are a master travel generator. You must respond with a raw JSON object containing "
                    "exactly two main keys: 'flight_coordinates' and 'days'. "
                    "The 'flight_coordinates' key must be an object with four keys: 'departure_lat', 'departure_lon', 'arrival_lat', and 'arrival_lon'. "
                    "The 'days' key must be a list where each item represents a single day and has exactly "
                    "six keys: 'title', 'morning', 'afternoon', 'evening', 'lat', and 'lon'. "
                    "Do not include any normal conversational text outside this raw JSON object structure."

                )
            },
            {"role": "user", "content": prompt}
        ]
    )
    

    return json.loads(response.choices.message.content)



def get_weather_forecast(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"

    parameters = {
        'latitude': lat,
        'longitude': lon,
        'daily': ["temperature_2m_max", "temperature_2m_min", "rain_sum", "wind_speed_10m_max"],
        'timezone': 'auto'
        }

    encoded_parameters = urllib.parse.urlencode(parameters, doseq=True)
    encoded_url = f"{url}?{encoded_parameters}"
    
    with urllib.request.urlopen(encoded_url) as response:
        request = json.loads(response.read().decode())

        daily_fore = request['daily']
        forecast = []

    for i in range(len(daily_fore['time'])):
        forecast.append({
            'day': f"Day {i+1}",
            'date': daily_fore['time'][i],
            'high_temp': daily_fore['temperature_2m_max'][i],
            'low_temp': daily_fore['temperature_2m_min'][i],   
            'rain': daily_fore['rain_sum'][i],
            'wind': daily_fore['wind_speed_10m_max'][i]
        })

    return forecast 

with st.sidebar.form('input_form'):

    location = st.text_input("What city do you live in?")
    destination = st.text_input("Destination:")
    dates = st.date_input("How long is your trip?", value=[])
    people = st.number_input("How many people are traveling?", min_value=1, step=1, value=1)
    budget = st.number_input("What is your maximum budget?", step=100, value=0)
    style = st.selectbox("What is your prefered travel style?", ["Budget / Backpacker", "Mid-Range / Comfort", "Luxury"])

    submit_button = st.form_submit_button(label="Generate Iterinary")

if submit_button:
    st.write("Processing Request...")

    tab1, tab2, tab3, tab4 = st.tabs(["Daily Schedule", "Route Map", "Weather Forecast", "Feasibility Calculator"])

    travel_days = (dates[1]-dates[0]).days + 1 if len(dates) == 2 else 3

    itinerary_data = generate_schedule(travel_days, destination, style)

    flight_coords = itinerary_data['flight_coordinates']
    ai_lat = flight_coords['arrival_lat']
    ai_lon = flight_coords['arrival_lon']

    carrier_name = "Delta Air lines"

    with tab1:
        st.write("Personalized travel plan:")

        for index, day_plan in enumerate(itinerary_data['days']):
            
          with st.expander(f"Day {index+1}: {day_plan['title']}"):
            st.write(f"Morning: {day_plan['morning']}")
            st.write(f"Afternoon: {day_plan['afternoon']}")
            st.write(f"Morning: {day_plan['evening']}")

    with tab2:
        st.write("Interactive Travel Pathway")
        
        route_points = []

        route_points.append({
            "name": f"🛫 {carrier_name} Flight",
            "lat": flight_coords['departure_lat'], 
            "lon": flight_coords['departure_lon'], 
            "info": f"Departure from {location}"
            })
        
        for idx, day_info in enumerate(itinerary_data['days']):
            route_points.append({
                "name": f"📍 Day {idx+1} Central Anchor",
                "lat": day_info['lat'],
                "lon": day_info['lon'],
                "info": day_info['title']
            })
        
        base_map = folium.Map(location=[route_points[0]['lat'], route_points[0]['lon']], zoom_start=14)

        path_coordinates = []

        for spot in route_points:
            coordinates = [spot['lat'], spot['lon']]
            path_coordinates.append(coordinates)

            popup_card = f"<b>{spot['name']}</b><br>{spot['info']}"

            folium.Marker(
                location=coordinates,
                popup=folium.Popup(popup_card, max_width=200),
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(base_map)

        folium.PolyLine(locations=path_coordinates, color="crimson", weight=3).add_to(base_map)

        st_folium(base_map, width=700, height=450)
    
    with tab3:
        st.write("Weather Dashboard")

        forecast_list = get_weather_forecast(lat=ai_lat, lon=ai_lon)

        has_rain = any(day_item['rain'] > 0.0 for day_item in forecast_list)
        has_heat = any(day_item['high_temp'] >= 35.0 for day_item in forecast_list)
        has_wind = any(day_item['wind'] >= 10.0 for day_item in forecast_list)

        if has_rain:
            st.warning("Precipitation Warning! Rain forecasted")
        if has_heat:
            st.error("Extreme heat in your area! Stay hydrated and protected")
        if has_wind:
            st.info("High amounts of wind detected! Staying indoors is recommended")    

        st.divider()           

        cols = st.columns(len(forecast_list))

        for index, day_info in enumerate(forecast_list):
            with cols[index]:
                st.markdown(f"{day_info['day']}")
                st.caption(f"{day_info['date']}")

                emoji = "🌧️" if day_info['rain'] > 0.0 else "☀️"
                st.markdown(f"## {emoji}")

                st.write(f" {day_info['high_temp']}°C / {day_info['low_temp']}°C")
                st.caption(f" {day_info['wind']} m/s")

    with tab4:
        st.write("Realism of trip:")

        trip_duration = (dates[1] - dates[0]).days + 1 if len(dates) == 2 else 5
        success_score = predict_budget_success(budget, trip_duration, people, style)

        metric_col1, metric_col2 = st.columns(2)
        
        with metric_col1:
            st.metric(label="Target Success Probability", value=f"{success_score}%")
        with metric_col2:
            if success_score >= 70:
                st.success("✅ Your budget matches your travel specifications.")
            else:
                st.error("⚠️ Risk Detected: Your budget configuration may result in cost overruns.")

        st.divider()

        st.write("Predicted Expense Allocation Breakdown")

        lodging_pct = st.slider("Lodging Allocation (%)", min_value=0, max_value=100, value=40)
        dining_pct = st.slider("Dining Allocation (%)", min_value=0, max_value=100, value=35)
        activity_pct = st.slider("Activities Allocation (%)", min_value=0, max_value=100, value=15)
        buffer_pct = st.slider("Emergency Buffer (%)", min_value=0, max_value=100, value=10)

        estimated_lodging = budget * (lodging_pct / 100)
        estimated_dining = budget * (dining_pct / 100)
        estimated_activities = budget * (activity_pct / 100)
        estimated_buffer = budget * (buffer_pct / 100)

        costs_array = [estimated_lodging, estimated_dining, estimated_activities, estimated_buffer]
        labels_list = ['Lodging', 'Dining', 'Activities', 'Emergency Buffer']
        chart_colors = ['#2b5c8f', '#e07a5f', '#f4f1de', '#81b29a']

        fig, ax = plt.subplots(figsize=(6, 4))

        ax.pie(
            costs_array, 
            labels=labels_list, 
            autopct='%1.1f%%', 
            startangle=140, 
            colors=chart_colors,
            textprops={'fontsize': 10}
        )

        ax.axis('equal')
        fig.patch.set_facecolor('none')

        st.pyplot(fig)
