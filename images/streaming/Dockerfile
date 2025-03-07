FROM python:3.9-slim

WORKDIR /app

# Αντιγραφή του traffic script

COPY streaming_traffic.py /app/

# Εγκατάσταση απαιτήσεων (αν χρειάζεται)

RUN pip install requests 

# Εκτέλεση του script

CMD ["python", "streaming_traffic.py"]
