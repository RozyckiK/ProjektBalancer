from flask import Flask, jsonify, render_template_string
from kafka import KafkaConsumer
import json
from threading import Thread
from collections import deque
from prometheus_client import start_http_server, Summary, Counter

# Metryki z etykietami
REQUEST_TIME = Summary('response_time_seconds', 'Czas odpowiedzi', ['endpoint'])
REQUEST_COUNT = Counter('requests_total', 'Liczba żądań HTTP', ['endpoint'])
ERROR_COUNT = Counter('http_errors_total', 'Liczba błędów HTTP', ['endpoint'])

# Start Prometheus metrics endpoint
start_http_server(8001, addr="0.0.0.0")

app = Flask(__name__)
messages = deque(maxlen=100)

def consume():
    print("Kafka consumer uruchomiony...")
    consumer = KafkaConsumer(
        "rowery",
        bootstrap_servers="kafka:9092",
        api_version=(0,11,5),
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset='latest',
        group_id="flask-group"
    )
    print("Konsumer połączony z Kafka.")
    for msg in consumer:
        print(f"Odebrano wiadomość: {msg.value}")
        messages.append(msg.value)

@app.route("/")
@REQUEST_TIME.labels(endpoint="/").time()
def home():
    REQUEST_COUNT.labels(endpoint="/").inc()
    try:
        html_template = """
        <h2>Ostatnie dane rowerów miejskich</h2>
        <table border="1" cellpadding="5">
            <tr>
                <th>Miasto</th>
                <th>ID roweru</th>
                <th>Szerokość (lat)</th>
                <th>Długość (lon)</th>
            </tr>
            {% for row in messages %}
            <tr>
                <td>{{ row["city"] }}</td>
                <td>{{ row["bike_id"] }}</td>
                <td>{{ row["lat"] }}</td>
                <td>{{ row["lon"] }}</td>
            </tr>
            {% endfor %}
        </table>
        <p><a href='/bikes'>Zobacz jako JSON</a></p>
        """
        return render_template_string(html_template, messages=list(messages))
    except Exception:
        ERROR_COUNT.labels(endpoint="/").inc()
        raise

@app.route("/bikes")
@REQUEST_TIME.labels(endpoint="/bikes").time()
def get_bikes():
    REQUEST_COUNT.labels(endpoint="/bikes").inc()
    try:
        return jsonify(list(messages))
    except Exception:
        ERROR_COUNT.labels(endpoint="/bikes").inc()
        raise

if __name__ == "__main__":
    Thread(target=consume, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)