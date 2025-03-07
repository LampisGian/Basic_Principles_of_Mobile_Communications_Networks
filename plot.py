
import matplotlib.pyplot as plt
import os
import time
import json
import math
import docker
import random
import subprocess
from tabulate import tabulate       
from collections import defaultdict
from base_station import BaseStation

def plot_grid(container_positions, container_connections, base_station_objects, base_station_colors ):

    plt.clf()  # Καθαρισμός του γραφήματος
    
    plt.gcf().set_size_inches(16, 8)

    # Εμφάνιση σταθμών βάσης ως τετράγωνα

    for i, bs in enumerate(base_station_objects):

        plt.scatter(
            *bs.position,
            c=base_station_colors[i],
            marker="s",  # Χρήση τετραγώνου
            s=200,
            label=f"{bs.name}"
        )

        # Προσθήκη ονόματος σταθμού βάσης

        plt.text(
            bs.position[0] + 2,  # Λίγο δεξιά από τον σταθμό βάσης
            bs.position[1],
            bs.name,
            fontsize=10,
            color=base_station_colors[i],
            weight="bold"
        )

    # Εμφάνιση containers

    for container, position in container_positions.items():

        if container in ["streaming_server_container", "gaming_server_container","video_server_container"]:

            # Ειδική εμφάνιση για servers

            plt.scatter(
                *position,
                c="green",  # Πράσινο χρώμα για τους servers
                marker="o",  # Κυκλικό marker
                s=200,  # Μεγαλύτερο μέγεθος
                label=f"{container} (Server)"
            )

            # Προσθήκη ονόματος server

            plt.text(
                position[0] + 2,  # Λίγο δεξιά από το server
                position[1],
                container,
                fontsize=9,
                color="green",
                weight="bold"
            )

        else:

            # Εμφάνιση για τα υπόλοιπα containers

            base_station_name = container_connections[container]

            base_station_index = int(base_station_name.split("_")[-1]) - 1  # Ανάκτηση index σταθμού βάσης

            plt.scatter(
                *position,
                c=base_station_colors[base_station_index],  # Ίδιο χρώμα με τον σταθμό βάσης
                label=f"{container}",
                s=50
            )

            # Προσθήκη ονόματος container

            plt.text(
                position[0] + 2,  # Λίγο δεξιά από το container
                position[1],
                container,
                fontsize=8,
                color="black",
                weight="normal"
            )

    # Ρυθμίσεις γραφήματος

    plt.xlim(0, 200)

    plt.ylim(0, 200)

    plt.grid(True)

    plt.title("Cellular Network Map")
    
    plt.pause(0.1)