import os
import polyline
from django.conf import settings
from rest_framework import views, status
from rest_framework.response import Response

from .services.route_service import RouteService
from .services.fuel_service import FuelService
from .services.map_service import MapService
from .serializers import RouteRequestSerializer


class PlanRouteView(views.APIView):
    def __init__(self):
        super().__init__()
        self.route_service = RouteService()
        self.fuel_service = FuelService()
        self.map_service = MapService()

    def post(self, request):
        # Step 1: Validate incoming JSON request using serializer
        serializer = RouteRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Step 2: Extract start and end location strings from validated data
        start_location = serializer.validated_data["start_location"]
        end_location = serializer.validated_data["end_location"]

        # Step 3: Convert location names to geographic coordinates
        start_coords = self.route_service.get_coordinates(start_location)
        end_coords = self.route_service.get_coordinates(end_location)

        if not start_coords or not end_coords:
            return Response(
                {"error": "Invalid locations"}, status=status.HTTP_400_BAD_REQUEST
            )

         # Step 4: Fetch route data (distance, duration, path)
        route_data = self.route_service.get_route(start_coords, end_coords)
        if not route_data:
            return Response(
                {"error": "Could not calculate route"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Step 5: Decode the polyline route into a list of lat/lon points
        points = polyline.decode(route_data["geometry"])

        # Step 6: Determine optimal fuel stops along the decoded route points
        fuel_stops = self.fuel_service.get_optimal_fuel_stops(points)

        # Step 7: Calculate total cost
        total_cost = self.fuel_service.calculate_total_cost(route_data['distance'], fuel_stops)

        # Step 8: Create a map object with route and fuel stop markers
        route_info = {"points": points, "distance": route_data["distance"]}
        m = self.map_service.generate_map(route_info, fuel_stops)

        # Step 9: Create a 'maps' directory inside BASE_DIR if it doesn't exist
        maps_directory = os.path.join(settings.BASE_DIR, "maps")
        os.makedirs(maps_directory, exist_ok=True)

        # Step 10: Save the generated map as an HTML file
        map_file = os.path.join(maps_directory, f"route.html")
        m.save(map_file)

        return Response(
            {
                "start_location": start_location,
                "end_location": end_location,
                "distance": route_data["distance"],
                "total_cost": total_cost,
                "fuel_stops": fuel_stops,
                "map_url": "/maps/route.html",
            }
        )
