import docker
import time

# Σύνδεση στο Docker
client = docker.from_env()

# Όνομα image
IMAGE_NAME = "video-player"

# Βρες όλα τα containers που χρησιμοποιούν το image
containers = client.containers.list(filters={"ancestor": IMAGE_NAME})

if not containers:
    print(f"Δεν υπάρχουν ενεργά containers με το image '{IMAGE_NAME}'.")
else:
    print(f"Βρέθηκαν {len(containers)} containers:\n")
    for container in containers:
        print(f"- {container.name}")

    print("\nΠαρακολούθηση logs σε πραγματικό χρόνο (πατήστε Ctrl+C για έξοδο)...\n")

    try:
        while True:
            for i, container in enumerate(containers):
                print(f"\033[{i + 1}H", end="")  # Μετακίνηση του cursor στη γραμμή i+1
                logs = container.logs(tail=1, stream=False).decode("utf-8").strip()  # Παίρνει την τελευταία γραμμή logs
                print(f"Container {container.name}: {logs}", end="")  # Εκτυπώνει τα logs
            time.sleep(1)  # Ενημέρωση κάθε 1 δευτερόλεπτο
    except KeyboardInterrupt:
        print("\nΤερματισμός παρακολούθησης logs.")
