
from flask import Flask, request

app = Flask(__name__)

@app.route('/upload', methods=['POST'])

def upload():

    data = request.data  # Πρόσβαση στα δεδομένα που στάλθηκαν στο αίτημα

    data_size = len(data)

    print(f"Streaming Server: Received {data_size} bytes", flush=True)

    return 'OK', 200  # Επιστροφή απάντησης με κωδικό κατάστασης 200 (OK)

if __name__ == "__main__":

    app.run(host='0.0.0.0', port=5001)
