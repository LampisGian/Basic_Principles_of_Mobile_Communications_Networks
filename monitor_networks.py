import subprocess
import json
import time
from tabulate import tabulate

# Λίστα δικτύων που μας ενδιαφέρουν

BASE_STATIONS = ["base_station_1", "base_station_2", "base_station_3"]

def get_network_containers(network_name):

    """Ανακτά τα containers που είναι συνδεδεμένα σε ένα συγκεκριμένο δίκτυο."""
      
    try:

        network_info = subprocess.check_output(f"docker network inspect {network_name}", shell=True).decode()

        network_data = json.loads(network_info)

        containers = network_data[0].get("Containers", {})

        return containers
    
    except subprocess.CalledProcessError as e:

        print(f"Error inspecting network {network_name}: {e}")

        return {}

def display_base_station_data():

    """Ανακτά και εμφανίζει δεδομένα για τα base stations."""

    table_data = []

    for base_station in BASE_STATIONS:

        containers = get_network_containers(base_station)

        container_names = [info.get("Name", "Unknown") for info in containers.values()]

        table_data.append([
            base_station,  # Όνομα δικτύου
            len(container_names),  # Αριθμός συνδεδεμένων containers
            "\n".join(container_names) if container_names else "None"  # Λίστα containers
        ])

    # Εμφάνιση αποτελεσμάτων σε πίνακα

    print("\033[H\033[J", end="")  # Καθαρισμός τερματικού

    print(tabulate(
        table_data,
        headers=["Base Station", "Connected Devices (#)", "Device Names"],
        tablefmt="fancy_grid"
    ))


def main():

    print("Monitoring base station networks...")

    while True:

        display_base_station_data()

        time.sleep(0.1)  # Ανανέωση κάθε 5 δευτερόλεπτα


if __name__ == "__main__":

    main()
