import requests
from geopy.geocoders import Nominatim

class RouteService:
    def __init__(self):
        self.OSRM_BASE_URL = 'http://router.project-osrm.org'
        self.geolocator = Nominatim(user_agent="route_planner")

    def get_coordinates(self, location):
        """
        Convert a location name into geographic coordinates (latitude, longitude).
        Returns None if location not found.
        """
        try:
            location_data = self.geolocator.geocode(location)
            if location_data:
                return {
                "lat": location_data.latitude,
                "lon": location_data.longitude
            }
        except Exception as e:
            print(f"Geocoding error for '{location}': {e}")
        return None

    def get_route(self, start_coords, end_coords):
        """
        Get route details between start and end coordinates using OSRM.
        Returns distance (miles), duration (hours), geometry (route path), and navigation steps.
        """
        url = f"{self.OSRM_BASE_URL}/route/v1/driving/{start_coords['lon']},{start_coords['lat']};{end_coords['lon']},{end_coords['lat']}"
        params = {'overview': 'full', 'geometries': 'polyline', 'steps': 'true'}
        response = requests.get(url, params=params)
        data = response.json()

        if data['code'] != 'Ok':
            raise ValueError("Could not calculate route")
        
        route = data['routes'][0]

        return {
            'distance': route['distance'] / 1609.34,  # meters → miles
            'duration': route['duration'] / 3600,     # seconds → hours
            'geometry': route['geometry'],
            'steps': route['legs'][0]['steps']
        }
