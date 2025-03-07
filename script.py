import docker
import os
import time

client = docker.from_env()

def create_network(name):
    try:
        client.networks.get(name)
    except docker.errors.NotFound:
        client.networks.create(name=name, driver="bridge")


def create_base_station_networks(base_station_names):
    for name in base_station_names:
        try:
            client.networks.get(name)
        except docker.errors.NotFound:
            client.networks.create(name=name, driver="bridge")


def build_images():

    """Χτίζει τα Docker images για servers, συσκευές, και πρόσθετα containers."""
    
    paths = {
        "gaming_server": "./servers/gaming_server",
        "streaming_server": "./servers/streaming_server",
        "gaming_device": "./images/gaming",
        "streaming_device": "./images/streaming",
        "browsing_device": "./images/browsing",
        "video_server": "./servers/video"
    }

    for image_name, path in paths.items():
        os.system(f"docker build -t {image_name}-image {path}")


def create_server_containers(network):

    """Δημιουργεί και εκκινεί τα containers των servers."""

    servers = [
        {"name": "gaming_server_container", "image": "gaming_server-image", "ports": {"8080/udp": 8080}},
        {"name": "streaming_server_container", "image": "streaming_server-image", "ports": {"5001/tcp": 5001}}
    ]

    for server in servers:
        try:
            container = client.containers.get(server["name"])
            if container.status != "running":
                container.start()
        except docker.errors.NotFound:
            client.containers.run(
                image=server["image"],
                name=server["name"],
                detach=True,
                network=network.name,
                ports=server["ports"]
            )


def create_device_containers(server_network, base_station_names):

    device_configs = [
        {"type": "gaming_device", "image": "gaming_device-image", "server_name": "gaming_server_container", "base_station": base_station_names[0]},
        {"type": "streaming_device", "image": "streaming_device-image", "server_name": "streaming_server_container", "base_station": base_station_names[1]}
        #{"type": "browsing_device", "image": "browsing_device-image", "base_station": base_station_names[2]}
        ]

    for config in device_configs:
        for i in range(1, 5):  # Δημιουργούμε 5 instances για κάθε τύπο
            device_name = f"{config['type']}_{i}"
            try:
                container = client.containers.get(device_name)
                if container.status != "running":
                    container.start()
            except docker.errors.NotFound:
                environment = {}
                if "server_name" in config:
                    server_container = client.containers.get(config["server_name"])
                    server_ip = server_container.attrs['NetworkSettings']['Networks'][server_network.name]['IPAddress']
                    environment = {
                        "SERVER_HOSTNAME": server_ip,
                        "SERVER_PORT": "5001"
                    }

                client.containers.run(
                    image=config["image"],
                    name=device_name,
                    detach=True,
                    network=server_network.name,
                    environment=environment
                )



def create_video_streaming_network():

    IMAGE_NAME = "video_server-image"
    NETWORK_NAME = "video_network"
    SENDER_NAME = "video_server_container"
    RECEIVER_PREFIX = "video_device"

    try: # Εκκίνηση αποστολέα δημιουργια video_streamer_container

        sender = client.containers.run(
            IMAGE_NAME,
            name=SENDER_NAME,
            network=NETWORK_NAME,
            detach=True,
            tty=True
        )

    except docker.errors.APIError as e:

        print(f"Σφάλμα κατά την εκκίνηση του αποστολέα: {e}")

    receivers = []  # Δημιουργία video_receivers

    for i in range(1, 5):  # 4 δέκτες

        receiver_name = f"{RECEIVER_PREFIX}_{i}"

        print(f"Δημιουργία δέκτη: {receiver_name}...")

        try:
            receiver = client.containers.run(
                IMAGE_NAME,
                command=["ffmpeg", "-i", "udp://224.0.0.1:1234", "-f", "null", "-"],
                name=receiver_name,
                network=NETWORK_NAME,
                detach=True,
                tty=True
            )

            receivers.append(receiver)

        except docker.errors.APIError as e:

            print(f"Σφάλμα κατά την εκκίνηση του δέκτη '{receiver_name}': {e}")



def cleanup_docker_resources():
        
    client = docker.from_env()    

    print("[Info] Διαγραφή όλων των containers...")

    containers = client.containers.list(all=True)

    for container in containers:

        try:
            container_name = container.name

            container.remove(force=True)

            print(f"[Deleted] Container '{container_name}' διαγράφηκε.")

        except Exception as e:

            print(f"[Error] Αποτυχία διαγραφής του container '{container.name}': {e}")


    print("\n[Info] Διαγραφή όλων των images...")  # Διαγραφή images

    images = client.images.list()

    for image in images:

        try:
            image_id = image.id

            image_name = image.tags if image.tags else image_id

            client.images.remove(image=image_id, force=True)

            print(f"[Deleted] Image '{image_name}' διαγράφηκε.")

        except Exception as e:

            print(f"[Error] Αποτυχία διαγραφής του image '{image.id}': {e}")

    print("\n[Info] Όλα τα resources του Docker καθαρίστηκαν.")



if __name__ == "__main__":

    cleanup_docker_resources()

    server_network_name = "server_network"

    video_network_name = "video_network"

    create_network(server_network_name)

    create_network(video_network_name)

    server_network = client.networks.get(server_network_name)

    # Δημιουργία δικτύων για base stations
    
    base_station_names = [f"base_station_{i}" for i in range(1, 4)]

    create_base_station_networks(base_station_names)

    build_images() # Δημιουργία όλων των Docker images

    create_server_containers(server_network)  # Δημιουργία containers για servers

    time.sleep(5)

    create_device_containers(server_network, base_station_names) # Δημιουργία containers για συσκευές
 
    create_video_streaming_network() # Δημιουργία video streaming containers

