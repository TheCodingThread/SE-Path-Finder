import tkinter as tk
from tkinter import ttk, messagebox
import requests
import folium
from geopy.geocoders import Nominatim
import webbrowser
import os

SPEEDS = {
    "car": None,     
    "bike": 50,      
    "walk": 5        
}

def get_coordinates(place):
    geolocator = Nominatim(user_agent="osrm_rajasthan_app")
    location = geolocator.geocode(place + ", Rajasthan, India") 
    if location:
        return (location.latitude, location.longitude)
    else:
        raise Exception(f"Location not found: {place}")

def get_osrm_route(start, end):
    url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}?overview=full&geometries=geojson"
    data = requests.get(url).json()

    if "routes" not in data:
        raise Exception("No route found")

    raw_route = data["routes"][0]
    distance = raw_route["distance"] / 1000     
    car_time = raw_route["duration"] / 60       
    coords = raw_route["geometry"]["coordinates"]

    coord_list = [(lat, lon) for lon, lat in coords]

    return coord_list, distance, car_time

def plot_map(route, start, end, distance, duration):
    m = folium.Map(location=route[0], zoom_start=7)
    folium.PolyLine(route, color="blue", weight=5).add_to(m)
    folium.Marker(route[0], icon=folium.Icon(color="green"), popup="Start").add_to(m)
    folium.Marker(route[-1], icon=folium.Icon(color="red"), popup="End").add_to(m)

    filename = "rajasthan_route_map.html"
    m.save(filename)
    return filename

def find_route():
    start_place = start_entry.get()
    end_place = end_entry.get()
    mode = mode_box.get().lower()

    if start_place.strip() == "" or end_place.strip() == "":
        messagebox.showerror("Error", "Please enter both start and end places.")
        return

    try:
        start_coords = get_coordinates(start_place)
        end_coords = get_coordinates(end_place)

        route, distance, car_time = get_osrm_route(start_coords, end_coords)

        if mode == "car":
            duration = car_time
        else:
            duration = (distance / SPEEDS[mode]) * 60

        result_label.config(
            text=f"Distance: {distance:.2f} km\nDuration ({mode.capitalize()}): {duration:.1f} mins"
        )

        map_file = plot_map(route, start_coords, end_coords, distance, duration)
        open_button.map_file = map_file
        open_button.config(state="normal")

    except Exception as e:
        messagebox.showerror("Error", str(e))

def open_map():
    webbrowser.open(open_button.map_file)

root = tk.Tk()
root.title("Rajasthan City Path Finder")
root.geometry("480x450")
root.resizable(False, False)

tk.Label(root, text="🗺️SE Path Finder", font=("Arial", 18, "bold")).pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Start Place:", font=("Arial", 12)).grid(row=0, column=0, sticky="w")
start_entry = tk.Entry(frame, font=("Arial", 12), width=25)
start_entry.grid(row=0, column=1, pady=5)

tk.Label(frame, text="End Place:", font=("Arial", 12)).grid(row=1, column=0, sticky="w")
end_entry = tk.Entry(frame, font=("Arial", 12), width=25)
end_entry.grid(row=1, column=1, pady=5)

tk.Label(frame, text="Mode:", font=("Arial", 12)).grid(row=2, column=0, sticky="w")
mode_box = ttk.Combobox(frame, values=["Car", "Bike", "Walk"], state="readonly", font=("Arial", 12))
mode_box.grid(row=2, column=1)
mode_box.current(0)

tk.Button(root, text="Find Route", font=("Arial", 14), bg="#0066cc", fg="white",
          command=find_route).pack(pady=20)

result_label = tk.Label(root, text="", font=("Arial", 12))
result_label.pack()

open_button = tk.Button(root, text="Open Map", state="disabled",
                        font=("Arial", 12), bg="green", fg="white", command=open_map)
open_button.pack(pady=15)

root.mainloop()
