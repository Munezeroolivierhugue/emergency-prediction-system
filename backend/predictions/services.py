from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import time

def get_location_from_coords(lat, lng):
    """
    Reverse geocodes latitude and longitude into a readable address string.
    Uses Nominatim (OpenStreetMap) with a custom user_agent.
    """
    # Initialize Nominatim API
    geolocator = Nominatim(user_agent="emergency_prediction_system_app")
    
    try:
        # We try to get the address, adding a short delay to respect API limits
        time.sleep(1)
        location = geolocator.reverse((lat, lng), exactly_one=True, timeout=5)
        
        if location and location.raw.get('address'):
            address = location.raw['address']
            
            # Construct a concise readable location
            parts = []
            
            # Try to get street/road level
            if 'road' in address:
                parts.append(address['road'])
            elif 'pedestrian' in address:
                parts.append(address['pedestrian'])
                
            # Try to get neighborhood/suburb
            if 'suburb' in address:
                parts.append(address['suburb'])
            elif 'neighbourhood' in address:
                parts.append(address['neighbourhood'])
                
            # Get city/town
            if 'city' in address:
                parts.append(address['city'])
            elif 'town' in address:
                parts.append(address['town'])
                
            if parts:
                return ", ".join(parts)
            else:
                return location.address.split(',')[0] # Fallback to first part of full address
                
        return "Unknown Location"
        
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        print(f"Geocoding error: {e}")
        return "Unknown Location"
    except Exception as e:
        print(f"Unexpected geocoding error: {e}")
        return "Unknown Location"
