import os
import time
import json
import math
import docker
import random
import subprocess
from plot import plot_grid
from tabulate import tabulate       
import matplotlib.pyplot as plt
from collections import defaultdict
from base_station import BaseStation

client = docker.from_env()

# Δίκτυα

server_network = "server_network"

server_containers = ["streaming_server_container", "gaming_server_container", "video_server_container"]  # Containers στο server network

base_station_colors = ["blue", "orange", "purple","green"]  # Χρώματα για κάθε σταθμό βάσης

base_station_positions = [(20, 50), (175, 100), (70, 180)]  # Θέσεις για τους σταθμούς βάσης

base_station_objects = [

    BaseStation(name=f"base_station_{i+1}", position=pos, max_bandwidth=50, max_containers=10)

    for i, pos in enumerate(base_station_positions)

]


def initialize_positions(containers):

    # Αρχικοποιεί τυχαίες θέσεις για τα containers

    return {container: (random.randint(0, 200), random.randint(0, 200)) for container in containers}


def update_positions_with_pattern(container_positions, pattern="linear", step=3):

    # Ενημερώνει τις θέσεις των containers με βάση ένα μοτίβο

    for container, (x, y) in container_positions.items():

        if container in server_containers:  # Εξαιρούμε τους servers
            continue

        if pattern == "linear":  # Γραμμική κίνηση: Κίνηση δεξιά

            container_positions[container] = ((x + step) % 200, y) # για να ήμαστε εντός ορίων 200*200



def calculate_distances(container_position):

    # Υπολογίζει τις αποστάσεις ενός container από όλους τους σταθμούς βάσης

    distances = {}

    for base_station in base_station_objects:

        distances[base_station.name] = base_station.calculate_distance(container_position)

    return distances



def signal_power(base_station, container_position, 
                 max_signal=10,      # Μέγιστη τιμή σήματος (π.χ., 10)
                 min_signal=1,       # Ελάχιστη τιμή σήματος (π.χ., 1)
                 max_distance=100,   # Απόσταση πέρα από την οποία το σήμα είναι ελάχιστο
                 min_distance=1):    # Ελάχιστη απόσταση 
 
    distance = max(base_station.calculate_distance(container_position), min_distance)

    normalized_distance = min(1, (distance - min_distance) / (max_distance - min_distance))

    # Αντιστροφή ποσοστού για το σήμα (όσο μικρότερη η απόσταση, τόσο μεγαλύτερο το σήμα)
    
    signal = max_signal - (normalized_distance * (max_signal - min_signal))

    return round(signal)  # Επιστροφή ακέραιας τιμής (π.χ., 1 έως 10)



def create_colored_signal_bar(signal_strength, max_signal=10, bar_length=10):

    # Κανονικοποίηση σε μήκος μπάρας

    filled_length = int(bar_length * (signal_strength / max_signal))

    empty_length = bar_length - filled_length

    if signal_strength > 8: color = "\033[1;92m"  

    elif signal_strength > 5:  color = "\033[1;93m" 

    else:  color = "\033[1;91m"  

    reset_color = "\033[1;0m"

    bar = f"{color}[{'*' * filled_length}{'-' * empty_length}] {signal_strength}/{max_signal}{reset_color}"
    
    return bar


########################################################################################################################
########################################################################################################################


# Initialize and manipulate the connection based on signal or distance


def initialize_container_connections(container_positions, container_connections):

    for container, position in container_positions.items():

        if container in ["streaming_server_container", "gaming_server_container", "video_server_container"]:

            continue  # Οι servers δεν αλλάζουν δίκτυα

        closest_base_station = determine_connection(container,position)

        current_network = container_connections.get(container)

        if closest_base_station != current_network:

            print(f"\n\033[1;35m[Initialization]\033[0m Connecting '\033[1;33m{container}\033[0m' to '\033[1;36m{closest_base_station}\033[0m'.")

            update_docker_network(container, current_network, closest_base_station)

            container_connections[container] = closest_base_station



def determine_connection(container_name, container_position):

    log_file_path = "./logs/connection_logs.txt"  # Ορισμός αρχείου καταγραφής

    SIGNAL_THRESHOLD = 5  # Ορισμός του κατωφλίου ισχύος
    
    best_station = None

    best_signal_strength = -float('inf')  # Εξασφαλίζουμε ότι θα βρούμε έναν καλύτερο σταθμό

    # Υπολογισμός της ισχύος σήματος για κάθε σταθμό βάσης

    for bs in base_station_objects:

        signal_strength = signal_power(bs, container_position)

        # Αν η ισχύς σήματος είναι πάνω από το κατώφλι, ελέγχουμε αν είναι η καλύτερη

        if signal_strength > SIGNAL_THRESHOLD:
            if signal_strength > best_signal_strength:
                best_signal_strength = signal_strength
                best_station = bs.name

    # Αν δεν βρεθεί σταθμός βάσης με αποδεκτή ισχύ, επιστρέφουμε τον πλησιέστερο

    if best_station is None:

        distances = calculate_distances(container_position)

        closest_base_station = min(distances, key=distances.get)

        # Καταγραφή μηνύματος στο αρχείο για επιλογή βάσει απόστασης

        message = (
            f"\n\033[1;35m[Connection]\033[0m Container '\033[1;34m{container_name}\033[0m' connected to"
            f"'\033[1;36m{closest_base_station}\033[0m' based on \033[1;33mminimum distance\033[0m "
            f"({distances[closest_base_station]:.2f} meters)."
        )

        with open(log_file_path, "a") as log_file:

            log_file.write(message)
        
        return closest_base_station

    # Καταγραφή μηνύματος στο αρχείο για επιλογή βάσει ισχύος σήματος

    message = (
        f"\n\033[1;35m[Connection]\033[0m Container '\033[1;34m{container_name}\033[0m' connected to "
        f"'\033[1;36m{best_station}\033[0m' based on \033[1;32msignal strength\033[0m "
        f"({best_signal_strength:.2f})."
    )

    with open(log_file_path, "a") as log_file:
        
        log_file.write(message)

    return best_station



def update_docker_network(container, current_network, new_network):

    try:

        # Αποσύνδεση από το τρέχον δίκτυο
        if current_network:
            subprocess.check_output(f"docker network disconnect {current_network} {container}", shell=True)
                
        subprocess.check_output(f"docker network connect {new_network} {container}", shell=True)

    except subprocess.CalledProcessError as e:

        print(f"[Error] Failed to update network for {container}: {e}")


########################################################################################################################
########################################################################################################################


def get_bandwidth_usage(container_name):
    
    try: 
        tx_cmd = f"docker exec {container_name} cat /sys/class/net/eth0/statistics/tx_bytes"
        rx_cmd = f"docker exec {container_name} cat /sys/class/net/eth0/statistics/rx_bytes"
        tx_bytes = int(subprocess.check_output(tx_cmd, shell=True).decode().strip())
        rx_bytes = int(subprocess.check_output(rx_cmd, shell=True).decode().strip())
        return tx_bytes, rx_bytes
    
    except Exception as e:

        print(f"Error fetching bandwidth usage for {container_name}: {e}")
        return 0, 0
    

def get_active_container_names():

    client = docker.from_env()

    containers = client.containers.list()  # Λίστα από ενεργά container objects

    return [container.name for container in containers]


def monitor_bandwidth():

    log_file_path = "./logs/monitor_logs.txt"

    log_cooldowns = "./logs/cooldown_logs.txt"
    
    # Αρχικοποίηση του αρχείου log

    with open(log_file_path, "w") as log_file:
        
        log_file.write("")
    
    # Λήψη των ενεργών containers

    containers = get_active_container_names()
    
    # Αρχικοποίηση θέσεων και συνδέσεων

    container_positions = initialize_positions(containers)

    container_connections = {container: None for container in containers}

    initialize_container_connections(container_positions, container_connections)
    
    # Αρχικοποίηση μεταβλητών για παρακολούθηση bandwidth

    last_tx = {container: 0 for container in containers}

    last_rx = {container: 0 for container in containers}
    
    # Λεξικό flags για αποφυγή ping-pong

    handover_flags = {container: 0 for container in containers} 
    
    # Μετρητές για handovers

    successful_handover_count = 0

    failed_handover_count = 0
    
    # Μετρητής για τον αριθμό των iterations

    iteration_count = 0
    
    interval = 1  # Διάστημα μεταξύ μετρήσεων σε δευτερόλεπτα
    

    while True:

        time.sleep(interval)  # Διάστημα μεταξύ μετρήσεων

        iteration_count += 1  # Αύξηση του μετρητή iterations
        
        # Μείωση του cooldown των flags

        for container in handover_flags:
            if handover_flags[container] > 0:
                handover_flags[container] -= 1
 
        update_positions_with_pattern(container_positions, pattern="linear", step=3)  # Ενημέρωση θέσεων containers
        
        # Αρχικοποίηση δομών για τα στατιστικά των base stations

        base_station_bandwidth = defaultdict(lambda: {"tx": 0, "rx": 0})

        base_station_containers = defaultdict(list)

        container_data = []

        container_bandwidth = defaultdict(dict)
                
        failed_handover_containers = []  # Λίστα για αποτυχίες handover σε αυτό το loop

        for container in containers:

            if container in ["streaming_server_container", "gaming_server_container", "video_server_container"]:
                 
                continue  # Αγνόηση συγκεκριμένων containers
            
            tx_bytes, rx_bytes = get_bandwidth_usage(container)
            
            # Υπολογισμός ρυθμού σε MB/s

            tx_rate = (tx_bytes - last_tx[container]) / 1024 / 1024 / interval
            rx_rate = (rx_bytes - last_rx[container]) / 1024 / 1024 / interval
            last_tx[container] = tx_bytes
            last_rx[container] = rx_bytes

            total_bandwidth = tx_rate + rx_rate
            
            position = container_positions[container]

            current_network = container_connections.get(container, None)
            
            # Έλεγχος αν πρέπει να ξεκινήσει η διαδικασία cooldown μετά από 3 iterations

            if iteration_count > 3:

                # Έλεγχος αν το container είναι σε cooldown
                
                if handover_flags[container] > 0:
                    
                    closest_base_station = current_network
                    
                    # Καταγραφή του status cooldown
                    
                    message = (
                        f"\n\033[1;31m[Cooldown]\033[0m Container '\033[1;34m{container}\033[0m' "
                        f"remains at '\033[1;36m{current_network}\033[0m' (Cooldown Active: {handover_flags[container]} iterations remaining).\n"
                    )
                    
                    with open(log_cooldowns, "a") as log_file:
                        log_file.write(message)
                
                else: 
                    
                    closest_base_station = determine_connection(container, position) # Καθορισμός του καλύτερου base station
            
            else:

                closest_base_station = current_network  # Για τις πρώτες 3 iterations, παραμένει στον τρέχοντα base station

            # Χρωματισμός για την εμφάνιση

            if handover_flags[container] > 0:

                container_display = f"\033[1;31m{container}\033[0m"  # Κόκκινο για cooldown
            
            else:

                container_display = f"\033[1;34m{container}\033[0m"  # Μπλε για κανονικά

            
            base_station_display = f"\033[1;36m{closest_base_station}\033[0m"  # Γαλάζιο για τα base stations
            
            # Αν υπάρχει αλλαγή base station και δεν είναι σε cooldown

            if closest_base_station != current_network and handover_flags[container] == 0 and iteration_count > 3:
                
                message = (
                    f"\n\033[1;35m[Handover]\033[0m Moving container '\033[1;34m{container}\033[0m' "
                    f"from '\033[1;36m{current_network}\033[0m' to '\033[1;36m{closest_base_station}\033[0m'.\n"
                )
                
                with open(log_file_path, "a") as log_file:
                    log_file.write(message)
                
                # Εκτέλεση handover

                update_docker_network(container, current_network, closest_base_station)

                container_connections[container] = closest_base_station
            
                successful_handover_count += 1  # Αύξηση του μετρητή επιτυχημένων handovers

            # Απόκτηση αντικειμένου base station και υπολογισμός signal strength

            if closest_base_station:
                base_station = next(bs for bs in base_station_objects if bs.name == closest_base_station)
                signal_strength = signal_power(base_station, position)
            
            else:
                signal_strength = 0  # Σε περίπτωση που δεν υπάρχει σύνδεση
                
            # Συγκέντρωση δεδομένων bandwidth

            if closest_base_station:

                base_station_bandwidth[closest_base_station]["tx"] += tx_rate
                base_station_bandwidth[closest_base_station]["rx"] += rx_rate
                base_station_containers[closest_base_station].append(container)
                container_bandwidth[closest_base_station][container] = total_bandwidth
            
            # Προσθήκη δεδομένων για εκτύπωση

            container_data.append(
                f"\n{container_display} - TX: {tx_rate:.2f} MB/s, RX: {rx_rate:.2f} MB/s, "
                f"Connected to: {base_station_display}, Signal Strength: {create_colored_signal_bar(signal_strength)}"
            )
        
        # Διαχείριση base stations που υπερβαίνουν το bandwidth

        for base_station_name in base_station_bandwidth.keys():

            bandwidth = base_station_bandwidth[base_station_name]

            connected_devices = base_station_containers[base_station_name]

            base_station_obj = next(bs for bs in base_station_objects if bs.name == base_station_name)

            used_bandwidth = bandwidth["tx"] + bandwidth["rx"]
            
            free_bandwidth = base_station_obj.max_bandwidth - used_bandwidth
            
            if used_bandwidth > base_station_obj.max_bandwidth and iteration_count > 3:
                
                # Εύρεση του container με το μεγαλύτερο bandwidth
                
                max_container, max_bandwidth = max(
                    container_bandwidth[base_station_name].items(),
                    key=lambda x: x[1]
                )
                
                # Καταγραφή προειδοποίησης και ενέργειας
                
                warning_message = (
                    f"\n\033[1;31m[Warning]\033[0m Base Station '\033[1;36m{base_station_name}\033[0m' "
                    f"exceeded max bandwidth!\n"
                )
                action_message = (
                    f"\n\033[1;92m[Action]\033[0m Container '\033[1;34m{max_container}\033[0m' "
                    f"with {max_bandwidth:.2f} MB/s needs to be moved.\n"
                )
                with open(log_file_path, "a") as log_file:
                    log_file.write(warning_message)
                    log_file.write(action_message)
                
                # Προσπάθεια εύρεσης άλλου base station με επαρκές bandwidth
               
                handover_successful = False
                
                for other_base_station in base_station_objects:
                    
                    if other_base_station.name == base_station_name:

                        continue
                    
                    other_used_bandwidth = sum(
                        base_station_bandwidth.get(other_base_station.name, {}).values()
                    )

                    other_free_bandwidth = other_base_station.max_bandwidth - other_used_bandwidth
                    
                    if other_free_bandwidth >= max_bandwidth and iteration_count > 3:
                        # Καταγραφή πρότασης
                       
                        suggestion_message = (
                            f"\n\033[1;34m[Suggestion]\033[0m Move container '\033[1;34m{max_container}\033[0m' "
                            f"to '\033[1;36m{other_base_station.name}\033[0m' "
                            f"(Free Bandwidth: {other_free_bandwidth:.2f} MB/s).\n"
                        )
                        
                        with open(log_file_path, "a") as log_file:
                            log_file.write(suggestion_message)
                        
                        # Εκτέλεση handover
                        
                        update_docker_network(max_container, base_station_name, other_base_station.name)
                        
                        container_connections[max_container] = other_base_station.name
                        
                        # Ενεργοποίηση flag για αποφυγή ping-pong
                        
                        handover_flags[max_container] = 10  # Cooldown για 10 iterations
                        
                        # Καταγραφή μετακίνησης
                        
                        moved_message = (
                            f"\n\033[1;92m[Action]\033[0m Container '\033[1;34m{max_container}\033[0m' "
                            f"moved to '\033[1;36m{other_base_station.name}\033[0m'.\n"
                        )
                        
                        with open(log_file_path, "a") as log_file:
                            log_file.write(moved_message)
                        
                        # Αύξηση του μετρητή επιτυχημένων handovers
                        
                        successful_handover_count += 1
                        
                        handover_successful = True
                        
                        break  # Έξοδος από τον for loop των base stations
                
                if not handover_successful:
                    
                    # Καταγραφή αποτυχίας handover
                    
                    failure_message = (
                        f"\n\033[1;31m[Handover Failure]\033[0m Container '\033[1;34m{max_container}\033[0m' "
                        f"could not be moved. Remaining at '\033[1;36m{base_station_name}\033[0m'.\n"
                    )
                    
                    with open(log_file_path, "a") as log_file:
                        log_file.write(failure_message)
                    
                    # Αύξηση του μετρητή αποτυχημένων handovers
                    failed_handover_count += 1
                
                    # Προσθήκη του container στη λίστα αποτυχιών για χρωματισμό στον πίνακα
                    failed_handover_containers.append(max_container)
        
        # Καθαρισμός οθόνης και εκτύπωση δεδομένων των containers
        print("\033[H\033[J", end="")


        ########################################################################################################
        ########################################################################################################

    
        # Εκτύπωση μετρητών handovers και handover success rate

        total_handovers = successful_handover_count + failed_handover_count

        if total_handovers > 0:
            success_rate = (successful_handover_count / total_handovers) * 100
        else:
            success_rate = 0.0
        
        GREEN_BOLD = "\033[1;32m"  # Έντονο Πράσινο
        RED_BOLD = "\033[1;31m"    # Έντονο Κόκκινο
        YELLOW_BOLD = "\033[1;33m" # Έντονο Κίτρινο
        RESET = "\033[0m"           # Επαναφορά στην προεπιλεγμένη μορφοποίηση

        print(f"\n\033[1mSuccessful Handovers:\033[0m {GREEN_BOLD}{successful_handover_count}{RESET} "
            f"\033[1mFailed Handovers:\033[0m {RED_BOLD}{failed_handover_count}{RESET} "
            f"\033[1mHandover Success Rate:\033[0m {YELLOW_BOLD}{success_rate:.2f}%{RESET}\n")

                
        # Εκτύπωση Containers

        print("\033[1mContainers :\033[0m")
        for i, data in enumerate(container_data, start=1):
            print(data)
            if i % 4 == 0:
                print()
        
        # Διαχείριση και εκτύπωση των base stations

        print("\033[1m\n\nBase Stations :\033[0m\n")
        table_data = []
        
        # Τα base stations ταξινομούνται με βάση το αριθμητικό μέρος του ονόματός τους

        sorted_base_stations = sorted(base_station_bandwidth.keys(), key=lambda x: int(x.split("_")[-1]))
        
        for base_station_name in sorted_base_stations:

            bandwidth = base_station_bandwidth[base_station_name]
            connected_devices = base_station_containers[base_station_name]
            base_station_obj = next(bs for bs in base_station_objects if bs.name == base_station_name)
            used_bandwidth = bandwidth["tx"] + bandwidth["rx"]
            free_bandwidth = base_station_obj.max_bandwidth - used_bandwidth
            
            # Χρωματισμός containers που έχουν αποτύχει να μετακινηθούν
            formatted_devices = [
                f"\033[1;31m{device}\033[0m" if device in failed_handover_containers else f"\033[1;34m{device}\033[0m"
                for device in connected_devices
            ]
            
            # Προσθήκη δεδομένων στον πίνακα
            table_data.append([
                f"\033[1;36m{base_station_name}\033[0m",
                f"{used_bandwidth:.2f} / {base_station_obj.max_bandwidth:.2f} MB/s",
                f"{bandwidth['tx']:.2f} MB/s",
                f"{bandwidth['rx']:.2f} MB/s",
                len(connected_devices),
                "\n".join(formatted_devices)
            ])
        
        # Εκτύπωση πίνακα base stations
        print(tabulate(
            table_data,
            headers=[
                "Base Station", 
                "Used/Max Bandwidth", 
                "TX (MB/s)", 
                "RX (MB/s)", 
                "Connected Devices (#)", 
                "Connected Device Names"
            ],
            tablefmt="fancy_grid"
        ))
        
        # Προαιρετικά, απενεργοποίηση της παρακολούθησης γραφικών:
        plot_grid(container_positions, container_connections, base_station_objects, base_station_colors)



########################################################################################################################
########################################################################################################################


# Initialize the environment

def disconnect_all_containers_from_base_stations(base_station_names):
 
    for base_station_name in base_station_names:
        try:
            network = client.networks.get(base_station_name)

            for container_id in network.attrs['Containers'].keys():

                container = client.containers.get(container_id)

                print(f"\n\033[1;31m[Disconnect]\033[0m Disconnecting container '\033[1;33m{container.name}\033[0m' from base station '\033[1;36m{base_station_name}\033[0m'...")

                network.disconnect(container, force=True)

        except docker.errors.NotFound:

            print(f"Base station network '{base_station_name}' not found.")



########################################################################################################################
########################################################################################################################



if __name__ == "__main__":

    # Αδειάζουμε τα base stations από containers

    base_station_names = ["base_station_1", "base_station_2", "base_station_3"]

    disconnect_all_containers_from_base_stations(base_station_names)

    plt.ion()  # Ενεργοποίηση interactive mode

    monitor_bandwidth()

