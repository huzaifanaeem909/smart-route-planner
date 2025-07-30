import os
import requests
from dotenv import load_dotenv
from geopy.distance import geodesic


class FuelService:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('DOE_API_KEY')
        self.base_url = ("https://developer.nrel.gov/api/alt-fuel-stations/v1/nearest.json")
        self.SEARCH_INTERVAL = 100  # Search every 100 miles

    def get_optimal_fuel_stops(self, route_points):
        """
        Identify optimal fuel stops at defined intervals along the route.
        param: route_points -> List of (lat, lon) tuples representing the route.
        return: List of optimal fuel stations.
        """
        fuel_stops = []
        last_search_point = 0
        current_distance = 0
        search_points = []

        # Determine the points along the route where we should search for stations
        for i in range(1, len(route_points)):
            point1 = route_points[i - 1]
            point2 = route_points[i]

            # Calculate distance between two consecutive route points
            segment_distance = geodesic(point1, point2).miles
            current_distance += segment_distance

            # If we've traveled SEARCH_INTERVAL miles, mark this as a search point
            if current_distance - last_search_point >= self.SEARCH_INTERVAL:
                search_points.append(point2)
                last_search_point = current_distance

        # Get stations near each search point
        for point in search_points:
            stations = self.get_fuel_stations(point[0], point[1], radius_miles=50)
            if stations:
                # Find closest station to route
                closest_station = min(
                    stations,
                    key=lambda x: geodesic(
                        (x["coords"][0], x["coords"][1]), point
                    ).miles,
                )
                fuel_stops.append(closest_station)

        return fuel_stops

    def get_fuel_stations(self, latitude, longitude, radius_miles=50):
        """
        Call the NREL API to retrieve public electric fuel stations within a given radius.
        return: List of formatted fuel station info dictionaries.
        """
        params = {
            "api_key": self.api_key,
            "latitude": latitude,
            "longitude": longitude,
            "radius": radius_miles,
            "fuel_type": "ELEC",  # Using ELEC for testing, You can change this to CNG, LPG, etc. as needed
            "status": "E",        # Only include stations that are currently in service
            "limit": 10,          # Max number of results per request
            "access": "public",   # Only show public access stations
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            stations = []

             # Check If the response contains a valid list of fuel stations
            if data and "fuel_stations" in data:
                for station in data["fuel_stations"]:
                    # Extract relevant station information and handle missing fields safely
                    stations.append(
                        {
                            "name": station.get("station_name", "Unknown Station"),
                            "coords": (
                                float(station.get("latitude", 0)),
                                float(station.get("longitude", 0)),
                            ),
                            "price": 0.5,
                            "address": station.get("street_address", ""),
                            "city": station.get("city", ""),
                            "state": station.get("state", ""),
                        }
                    )
            return stations

        except requests.exceptions.RequestException as e:
            print(f"Error fetching fuel stations: {e}")
            return []

    def calculate_total_cost(self, distance, charging_stations, miles_per_kwh=3.5):
        """Calculate the total estimated fuel cost for the trip"""
        if not charging_stations:
            return 0.0
        
        avg_price = sum(stop['price'] for stop in charging_stations) / len(charging_stations)
        kwh_needed = distance / miles_per_kwh
        total_cost = kwh_needed * avg_price
        return round(total_cost, 2)
