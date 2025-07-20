from math import sqrt

def euclidean_distance(loc1, loc2):
    """
    loc1, loc2: (x, y) tuples representing coordinates
    Returns Euclidean distance between loc1 and loc2
    """
    return sqrt((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2)

# Stub for future Google Maps integration
class GeoService:
    @staticmethod
    def get_distance(loc1, loc2):
        return euclidean_distance(loc1, loc2) 