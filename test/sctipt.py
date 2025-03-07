import docker
import time

# Σύνδεση στο Docker
client = docker.from_env()

# Ορισμός παραμέτρων
IMAGE_NAME = "video-player"
NETWORK_NAME = "video_network"
SENDER_NAME = "video_streamer"
RECEIVER_PREFIX = "video_receiver"

# Δημιουργία δικτύου
try:
    network = client.networks.create(NETWORK_NAME, driver="bridge")
    print(f"Δίκτυο '{NETWORK_NAME}' δημιουργήθηκε.")
except docker.errors.APIError:
    print(f"Το δίκτυο '{NETWORK_NAME}' υπάρχει ήδη.")
    network = client.networks.get(NETWORK_NAME)

# Εκκίνηση αποστολέα
try:
    sender = client.containers.run(
        IMAGE_NAME,
        name=SENDER_NAME,
        network=NETWORK_NAME,
        detach=True,
        tty=True  # Για debugging αν χρειαστεί
    )
    print(f"Container '{SENDER_NAME}' ξεκίνησε και αποστέλλει stream.")
except docker.errors.APIError as e:
    print(f"Σφάλμα κατά την εκκίνηση του αποστολέα: {e}")

# Δημιουργία δέκτες
receivers = []
for i in range(1, 4):  # Τρεις δέκτες
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
        print(f"Container '{receiver_name}' ξεκίνησε και λαμβάνει stream.")
    except docker.errors.APIError as e:
        print(f"Σφάλμα κατά την εκκίνηση του δέκτη '{receiver_name}': {e}")

