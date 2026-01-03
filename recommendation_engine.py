import pandas as pd
import numpy as np
from geopy.distance import geodesic

# Sample City Coordinates for Distance Calculation
# In a production app, these would be fetched via an API or Geocoding library
CITY_COORDS = {
    'Delhi': (28.6139, 77.2090),
    'Mumbai': (19.0760, 72.8777),
    'Bangalore': (12.9716, 77.5946),
    'Jaipur': (26.9124, 75.7873),
    'Agra': (27.1767, 78.0081),
    'Kochi': (9.9312, 76.2673),
    'Chennai': (13.0827, 80.2707)
}

class TravelRecommender:
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)
        # Pre-process: Drop rows with missing ratings/popularity
        self.df = self.df.dropna(subset=['Google review rating', 'Number of google review in lakhs'])
        
    def calculate_distance(self, source_city, dest_city):
        if source_city in CITY_COORDS and dest_city in CITY_COORDS:
            return geodesic(CITY_COORDS[source_city], CITY_COORDS[dest_city]).km
        return 500  # Default fallback distance for demonstration

    def get_recommendations(self, source_city, max_dist=500, top_n=5):
        data = self.df.copy()
        
        # 1. Calculate Distances
        data['Distance'] = data['City'].apply(lambda x: self.calculate_distance(source_city, x))
        
        # 2. Filter for Weekend Trips (Distance <= max_dist)
        weekend_options = data[data['Distance'] <= max_dist].copy()
        
        if weekend_options.empty:
            return "No destinations found within the weekend radius."

        # 3. Normalize Features (0 to 1 scale)
        def normalize(col):
            return (col - col.min()) / (col.max() - col.min())

        weekend_options['norm_rating'] = normalize(weekend_options['Google review rating'])
        weekend_options['norm_pop'] = normalize(weekend_options['Number of google review in lakhs'])
        weekend_options['norm_dist'] = 1 - normalize(weekend_options['Distance']) # Lower distance is better

        # 4. Calculate Final Score
        # Weights: Rating (40%), Popularity (30%), Proximity (30%)
        weekend_options['Score'] = (
            (weekend_options['norm_rating'] * 0.4) + 
            (weekend_options['norm_pop'] * 0.3) + 
            (weekend_options['norm_dist'] * 0.3)
        )

        # 5. Rank and Format
        result = weekend_options.sort_values(by='Score', ascending=False).head(top_n)
        return result[['Name', 'City', 'Distance', 'Google review rating', 'Score']]

# Example Usage
recommender = TravelRecommender('travel_places_india.csv')
print(recommender.get_recommendations('Chennai'))