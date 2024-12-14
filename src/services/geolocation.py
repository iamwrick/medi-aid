# src/services/geolocation.py
from typing import Dict, Tuple, List
from geopy.distance import geodesic
from src.utils.logger import get_logger

logger = get_logger(__name__)


class GeolocationService:
    def calculate_distance(
            self,
            point1: Tuple[float, float],
            point2: Tuple[float, float]
    ) -> float:
        """
        Calculate distance between two points in kilometers.
        """
        try:
            return geodesic(point1, point2).kilometers
        except Exception as e:
            logger.error(f"Error calculating distance: {str(e)}")
            raise

    def find_nearest_resources(
            self,
            incident_location: Tuple[float, float],
            resources: List[Dict],
            max_distance: float = None
    ) -> List[Dict]:
        """
        Find nearest resources within optional max_distance.
        Returns sorted list of resources with distances.
        """
        try:
            resources_with_distances = []
            for resource in resources:
                resource_location = (
                    resource['location']['lat'],
                    resource['location']['lng']
                )
                distance = self.calculate_distance(
                    incident_location,
                    resource_location
                )

                if max_distance is None or distance <= max_distance:
                    resources_with_distances.append({
                        **resource,
                        'distance': distance
                    })

            return sorted(
                resources_with_distances,
                key=lambda x: x['distance']
            )

        except Exception as e:
            logger.error(f"Error finding nearest resources: {str(e)}")
            raise