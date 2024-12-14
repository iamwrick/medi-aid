from typing import Dict, Tuple, List
import googlemaps
from datetime import datetime
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


class MapsService:
    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Get API key
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not self.api_key:
            logger.error("Google Maps API key not found in environment variables")
            raise ValueError("Google Maps API key not configured")

        try:
            self.gmaps = googlemaps.Client(key=self.api_key)
            logger.info("Google Maps client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Maps client: {str(e)}")
            raise

    def get_nearest_hospital(self, location: Tuple[float, float], radius: int = 5000) -> Dict:
        """Find the nearest hospital within radius (meters)"""
        try:
            logger.debug(f"Searching for hospitals near {location}")

            # Use places nearby search
            places_result = self.gmaps.places_nearby(
                location=location,
                radius=radius,
                keyword='hospital',
                type='hospital'
            )

            logger.debug(f"Places API response: {places_result}")

            if places_result and 'results' in places_result and places_result['results']:
                hospitals = places_result['results']
                # Sort by rating if available
                sorted_hospitals = sorted(
                    hospitals,
                    key=lambda x: x.get('rating', 0),
                    reverse=True
                )
                return sorted_hospitals[0]

            logger.warning(f"No hospitals found near {location}")
            return None

        except Exception as e:
            logger.error(f"Error in get_nearest_hospital: {str(e)}")
            return None

    def get_location_details(self, location: Tuple[float, float]) -> Dict:
        """Get detailed information about a location"""
        try:
            logger.debug(f"Getting location details for {location}")

            # Get reverse geocoding results
            reverse_geocode_result = self.gmaps.reverse_geocode(location)

            logger.debug(f"Reverse geocode response: {reverse_geocode_result}")

            if reverse_geocode_result:
                address = reverse_geocode_result[0]
                return {
                    'formatted_address': address.get('formatted_address', 'Unknown'),
                    'place_id': address.get('place_id', ''),
                    'location_type': address.get('geometry', {}).get('location_type', ''),
                    'components': address.get('address_components', [])
                }

            logger.warning(f"No location details found for {location}")
            return None

        except Exception as e:
            logger.error(f"Error in get_location_details: {str(e)}")
            return None