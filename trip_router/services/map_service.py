import folium
import hashlib
from django.core.cache import cache

class MapService:
    """Service for handling map generation operations"""
    
    @staticmethod
    def _get_cache_key(route_data):
        """
        Generate a unique cache key based on route data
        Create a unique string from start and end coordinates
        """
        start = route_data['points'][0]
        end = route_data['points'][-1]
        key_data = f"{start}{end}"
        return f"map_{hashlib.md5(key_data.encode()).hexdigest()}"

    @staticmethod
    def generate_map(route_data, fuel_stops):
        """
        Generate a Folium map showing the route and nearby fuel stations.
        Uses caching to avoid regenerating maps for the same route.
        """
        # Try to get cached map
        cache_key = MapService._get_cache_key(route_data)
        cached_map = cache.get(cache_key)
        
        if cached_map:
            return cached_map  # Return cached map if available
            
        start_coords = route_data['points'][0]
        end_coords = route_data['points'][-1]
        
        # Create map centered on start point
        m = folium.Map(location=start_coords, zoom_start=6)
        
        # Add route line
        folium.PolyLine(
            route_data['points'], 
            weight=2, 
            color='blue', 
            opacity=0.8
        ).add_to(m)
        
        # Add start/end markers
        folium.Marker(
            start_coords, 
            popup='Start', 
            icon=folium.Icon(color='green', icon='play')
        ).add_to(m)
        
        folium.Marker(
            end_coords, 
            popup='End', 
            icon=folium.Icon(color='red', icon='stop')
        ).add_to(m)
        
        # Add fuel stop markers
        for stop in fuel_stops:
            coords = (stop['coords'][0], stop['coords'][1])
            popup_content = f"""
                <b>{stop['name']}</b><br>
                Price: ${stop['price']:.2f}/gallon
            """
            
            folium.Marker(
                location=coords,
                popup=folium.Popup(popup_content, max_width=300),
                icon=folium.Icon(color='blue', icon='fa-gas-pump', prefix='fa')
            ).add_to(m)
        
        # Cache the generated map
        cache.set(cache_key, m, timeout=3600)  # Cache for 1 hour
        
        return m
