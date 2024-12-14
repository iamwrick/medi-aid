from dotenv import load_dotenv
import os
import googlemaps
from datetime import datetime
import json
from typing import Dict, Tuple


class GoogleMapsAPITester:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY')

        if not self.api_key:
            raise ValueError("Google Maps API key not found in .env file")

        # Initialize Google Maps client
        self.gmaps = googlemaps.Client(key=self.api_key)

        # Test locations (New York City locations)
        self.test_locations = [
            {
                "name": "Central Park",
                "coords": (40.7829, -73.9654)
            },
            {
                "name": "Times Square",
                "coords": (40.7484, -73.9857)
            }
        ]

    def test_geocoding(self) -> bool:
        """Test geocoding functionality"""
        print("\nTesting Geocoding...")
        try:
            # Forward geocoding
            result = self.gmaps.geocode("Central Park, New York")
            print(f"Forward Geocoding Result:")
            print(json.dumps(result[0] if result else "No results", indent=2))

            # Reverse geocoding
            result = self.gmaps.reverse_geocode((40.7829, -73.9654))
            print(f"\nReverse Geocoding Result:")
            print(json.dumps(result[0] if result else "No results", indent=2))

            return True
        except Exception as e:
            print(f"Geocoding test failed: {str(e)}")
            return False

    def test_places_nearby(self) -> bool:
        """Test places nearby search"""
        print("\nTesting Places Nearby Search...")
        try:
            result = self.gmaps.places_nearby(
                location=self.test_locations[0]["coords"],
                radius=2000,
                keyword='hospital'
            )

            print(f"Found {len(result.get('results', []))} nearby hospitals:")
            for place in result.get('results', [])[:3]:  # Show first 3 results
                print(f"\nHospital: {place.get('name')}")
                print(f"Address: {place.get('vicinity')}")
                print(f"Rating: {place.get('rating', 'N/A')}")

            return True
        except Exception as e:
            print(f"Places nearby test failed: {str(e)}")
            return False

    def test_distance_matrix(self) -> bool:
        """Test distance matrix calculations"""
        print("\nTesting Distance Matrix...")
        try:
            origins = [self.test_locations[0]["coords"]]
            destinations = [loc["coords"] for loc in self.test_locations]

            result = self.gmaps.distance_matrix(
                origins=origins,
                destinations=destinations,
                mode="driving",
                departure_time=datetime.now()
            )

            print(f"Distance Matrix Result:")
            print(json.dumps(result, indent=2))

            return True
        except Exception as e:
            print(f"Distance matrix test failed: {str(e)}")
            return False

    def test_directions(self) -> bool:
        """Test directions service"""
        print("\nTesting Directions...")
        try:
            result = self.gmaps.directions(
                origin=self.test_locations[0]["coords"],
                destination=self.test_locations[1]["coords"],
                mode="driving",
                alternatives=True
            )

            if result:
                route = result[0]
                print(f"Route found:")
                print(f"Duration: {route['legs'][0]['duration']['text']}")
                print(f"Distance: {route['legs'][0]['distance']['text']}")
                print(f"Steps: {len(route['legs'][0]['steps'])}")

            return True
        except Exception as e:
            print(f"Directions test failed: {str(e)}")
            return False


def main():
    print("=== Google Maps API Test ===")

    try:
        tester = GoogleMapsAPITester()
        print(f"\nAPI Key found: {tester.api_key[:5]}...{tester.api_key[-4:]}")

        # Run all tests
        tests = {
            "Geocoding": tester.test_geocoding,
            "Places Nearby": tester.test_places_nearby,
            "Distance Matrix": tester.test_distance_matrix,
            "Directions": tester.test_directions
        }

        results = {}
        for test_name, test_func in tests.items():
            print(f"\n{'-' * 50}")
            print(f"Running {test_name} test...")
            try:
                result = test_func()
                results[test_name] = "✓ Passed" if result else "✗ Failed"
            except Exception as e:
                results[test_name] = f"✗ Error: {str(e)}"

        # Print summary
        print("\n=== Test Summary ===")
        for test_name, result in results.items():
            print(f"{test_name}: {result}")

    except Exception as e:
        print(f"\n❌ Setup Error: {str(e)}")
        print("Please check your .env file and API key configuration.")


if __name__ == "__main__":
    main()