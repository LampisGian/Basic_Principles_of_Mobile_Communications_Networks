import math

class BaseStation:

    def __init__(self, name, position, max_bandwidth, max_containers):
        
        self.name = name
        self.position = position              # (x, y) θέση
        self.max_bandwidth = max_bandwidth    # Μέγιστο εύρος ζώνης
        self.max_containers = max_containers  # Μέγιστος αριθμός containers
        self.connected_containers = {}        # Λεξικό για συνδεδεμένα containers {container_name: bandwidth_usage}


    def calculate_distance(self, container_position):
  
        x1, y1 = self.position

        x2, y2 = container_position

        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

