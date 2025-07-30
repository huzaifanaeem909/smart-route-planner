# Smart Route Planner API

## Overview
This Django application provides an API designed to calculate and display:
1. The optimal route between a start and finish location within the USA.
2. Cost-effective fuel stops along the route, based on prices.
3. The total fuel cost for the journey, considering the vehicle's fuel efficiency and range.

## Key Features
- Route generation using OSRM (Open Source Routing Machine)
- EV charging station locations via NREL (National Renewable Energy Laboratory) API
- Cost calculation based on:
  - Distance traveled
  - EV efficiency (3.5 miles per kWh default)
  - Charging costs ($0.50 per kWh default)
- Interactive map showing route and charging stations

## Example Map
Below is an example of the route map with marked fuel stops:

![Route Map](https://github.com/huzaifanaeem909/smart-route-planner/blob/main/LA_NY.png)

## How It Works
1. **Input**: Users provide a start and finish location within the USA.
2. **Route Calculation**: The API calculates the best route using a free map and routing service.
3. **Fuel Stop Optimization**:
   - Route is divided into 100-mile segments
   - NREL API searches for charging stations near each segment based on:
     - Distance from route (≤ 20 miles radius)
     - Public accessibility
     - Operational status
4. **Output**:
   - A map showing the route and marked refueling stops.
   - A JSON response summarizing the total fuel cost and other details.

## Prerequisites
- Python 3.8+
- DOE API key for NREL database access
- Install dependencies listed in `requirements.txt`.


## Setup Instructions
1. Clone the repository:
   ```bash
   git clone git@github.com:huzaifanaeem909/smart-route-planner.git
   cd smart-route-planner
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create .env file in project root:
   ```
   DOE_API_KEY=your_api_key_here
   ```
5. Run the server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints
### 1. **Calculate Route and Fuel Stops**
   **Endpoint**: `/api/plan-route/`
   
   **Method**: POST
   
   **Request Body**:
   ```json
   {
       "start_location": "New York, NY",
       "end_location": "Los Angeles, CA"
   }
   ```
   
   **Response**:
   ```json
   {
    "route_coordinates": ["Coordinates between start and end location"],
    "map_url": "URL-to-route-map",
    "fuel_stops": ["Fuel stops along the route"],
    "total_cost": 123.45,
    "total_distance": 500.0
}
   ```

## Technologies Used
- **Backend Framework**: Django + Django REST Framework
- **Route Planning**: OSRM API
- **Fuel Stations**: NREL API
- **Mapping**: Folium
- **Geocoding**: Geopy
- **Environment Variables**: python-dotenv

## Project Structure
```
smart-route-planner/
├── trip_router/
│   ├── services/
│   │   ├── route_service.py    # Handles routing logic
│   │   ├── fuel_service.py     # Manages charging station data
│   │   └── map_service.py      # Generates route maps
│   ├── views.py                # API endpoints
│   └── serializers.py          # Request/response serialization
├── maps/                       # Generated route maps
├── requirements.txt            # Project dependencies
└── .env                       # Environment variables
```

## Future Enhancements
- Support for different fuel efficiency values.
- Dynamic vehicle range input.
- Enhanced UI for route and fuel stop visualization.
- Integration with real-time fuel price APIs.


## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

Feel free to reach out with questions or suggestions!
