#from weather_data.py import API
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
from scipy.stats import norm

st.set_page_config(layout="wide")
st.title("Iterinary Planner")

if "itinerary_data" not in st.session_state:
    st.session_state.itinerary_data = None
if "travel_days" not in st.session_state:
    st.session_state.travel_days = 3

def predict_budget_success(user_budget, trip_days, group_size, travel_style):
    try:
        style_mapping = {"Budget / Backpacker": 40.0, "Mid-Range / Comfort": 120.0, "Luxury": 350.0}
        style_cost_multiplier = style_mapping.get(travel_style, 120.0)
        
        lodging_and_daily_cost = trip_days * group_size * style_cost_multiplier
        
        flight_mean = 500.0 * group_size
        flight_std = 150.0 * np.sqrt(group_size) 
        
        expected_base_cost = lodging_and_daily_cost + flight_mean
        
        estimated_total_std = flight_std + (expected_base_cost * 0.08) 
        
        if estimated_total_std == 0:
            return 100 if user_budget >= expected_base_cost else 0
            
        z_score = (user_budget - expected_base_cost) / estimated_total_std
        success_probability = norm.cdf(z_score)
        
        success_percent = max(1, min(99, int(success_probability * 100)))

        recommended_budget = int(expected_base_cost + (1.04 * estimated_total_std))
        recommended_budget = int(np.round(recommended_budget / 10) * 10)

        return success_percent, recommended_budget

    except Exception as e:
        print(f"Math calculation error: {e}")
        return 84
        
def generate_schedule(dates, destination, style):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key = st.secrets["OPENROUTER_API_KEY"]
        )
    prompt = f"Create a {dates} day itinerary for {destination} tailored to a {style} style."

    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        response_format = {"type": "json_object"},
        messages = [
         {
                "role": "system", 
                "content": (
                    "You are an elite, hyper-detailed luxury travel concierge. You must respond with a raw JSON object containing "
                    "exactly two main keys: 'flight_coordinates' and 'days'. "
                    "The 'flight_coordinates' key must be an object with four keys: 'departure_lat', 'departure_lon', 'arrival_lat', and 'arrival_lon'. "
                    "The 'days' key must be a list where each item represents a single day and has exactly "
                    "six keys: 'title', 'morning', 'afternoon', 'evening', 'lat', and 'lon'. "
                    "CRITICAL GEOGRAPHY REQUIREMENT: The 'lat' and 'lon' for each day MUST be the exact, unique coordinates of that specific day's main attraction. Do NOT repeat the general city-center coordinates across multiple days. Every single day must have distinctly different coordinates.You MUST include every single key exactly as named. Do NOT omit 'lat' or 'lon' under any circumstances, even if you have to estimate the coordinates. Every single day object MUST contain exactly those six keys, no exceptions."
                    
                    "CRITICAL CONTENT REQUIREMENT: The descriptions for 'morning', 'afternoon', and 'evening' must be deep, complex, and immersive, including specific travel paths(bus numbers, streets, etc) "
                    "(at least 3-4 dense sentences each). Include highly specific landmark names, neighborhoods, recommended local foods or dishes "
                    "matching the requested travel style, realistic cultural context, and practical navigation tips (e.g., specific train lines or walking paths). "
                    "Avoid generic phrases like 'explore the area' or 'find a local eatery'—name actual types of locations, culinary specialties, and experiential details. "
                    "Do not include any normal conversational text outside this raw JSON object structure."
                )
            },
            {"role": "user", "content": prompt}
        ]
    )
    

    return json.loads(response.choices[0].message.content)



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

    location = st.text_input("What city do you live in?", key="user_location")
    destination = st.text_input("Destination:", key="user_destination")
    dates = st.date_input("How long is your trip?", value=[], key="form_dates")
    people = st.number_input("How many people are traveling?", min_value=1, step=1, value=1, key="user_people")
    budget = st.number_input("What is your maximum budget?", step=100, value=0, key="user_budget")
    style = st.selectbox("What is your prefered travel style?", ["Budget / Backpacker", "Mid-Range / Comfort", "Luxury"], key="user_style")

    submit_button = st.form_submit_button(label="Generate Iterinary")

if submit_button:
    
    if not st.session_state.form_dates or len(st.session_state.form_dates) < 2:
        st.error("Please pick both a Start Date and an End Date in the calendar before generating your itinerary!")
    else:
        st.session_state.itinerary_data = None

        with st.spinner("Processing Request & Fetching Travel Insights..."):
            start_dt = st.session_state.form_dates[0]
            end_dt = st.session_state.form_dates[1]
            st.session_state.travel_days = (end_dt - start_dt).days + 1
            
            st.session_state.itinerary_data = generate_schedule(
                st.session_state.travel_days, 
                st.session_state.user_destination, 
                st.session_state.user_style
            )

        st.rerun()

if st.session_state.itinerary_data is not None:

    tab1, tab2, tab3, tab4 = st.tabs(["Daily Schedule", "Route Map", "Weather Forecast", "Feasibility Calculator"])

    itinerary_data = st.session_state.itinerary_data
    travel_days = st.session_state.travel_days

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
                st.write(f"Evening: {day_plan['evening']}")

    with tab2:
        st.write("Interactive Travel Pathway")
        
        route_points = []

        route_points.append({
            "name": f"🛫 {carrier_name} Flight",
            "lat": flight_coords['departure_lat'], 
            "lon": flight_coords['departure_lon'], 
            "info": f"Departure from {st.session_state.user_location}"
            })

            
        
        for idx, day_info in enumerate(itinerary_data['days']):
            
            route_points.append({
                "name": f"📍 Day {idx+1} Central Anchor",
                "lat": day_info['lat'],
                "lon": day_info['lon'],
                "info": day_info['title']
            })
        
        base_map = folium.Map(location=[ai_lat, ai_lon], zoom_start=11)

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

        st_folium(base_map, width=1000, height=550, key="itinerary_map", returned_objects=[])
    
    with tab3:
        st.write("Weather Dashboard")
        
        forecast_list = get_weather_forecast(lat=ai_lat, lon=ai_lon)

        if forecast_list and len(forecast_list) > 0:
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

            weather_cols = st.columns(min(len(forecast_list), 7))

            for index, day_info in enumerate(forecast_list[:7]):
                with weather_cols[index]:
                    st.markdown(f"{day_info['day']}")
                    st.caption(f"{day_info['date']}")

                    emoji = "🌧️" if day_info['rain'] > 0.0 else "☀️"
                    st.markdown(f"## {emoji}")

                    st.write(f" {day_info['high_temp']}°C / {day_info['low_temp']}°C")
                    st.caption(f" {day_info['wind']} m/s")

    with tab4:
        st.write("Realism of trip:")

        trip_duration = (dates[1] - dates[0]).days + 1 if len(dates) == 2 else 5
        success_score, recommended_budget = predict_budget_success(
            st.session_state.user_budget, 
            travel_days, 
            st.session_state.user_people, 
            st.session_state.user_style
        )

        metric_col1, metric_col2 = st.columns(2)
        
        with metric_col1:
            st.metric(label="Target Success Probability", value=f"{success_score}%")
        with metric_col2:
            if success_score >= 70:
                st.success("✅ Your budget matches your travel specifications.")
            else:
                st.error("⚠️ Risk Detected: Your budget configuration may result in cost overruns."
                        f"To secure an 85% safety score, we recommend aiming for **${recommended_budget:,}**."
                )

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
