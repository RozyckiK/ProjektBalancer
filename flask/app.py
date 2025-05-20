from flask import Flask, jsonify, render_template_string
from kafka import KafkaConsumer
import json
from threading import Thread
from collections import deque

app = Flask(__name__)
messages = deque(maxlen=10)  # przechowujemy ostatnie 10 wiadomości

def consume():
    print("👂 Kafka consumer uruchomiony...")
    consumer = KafkaConsumer(
        "rowery",
        bootstrap_servers="kafka:9092",
        api_version=(0,11,5),
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset='latest',
        group_id="flask-group"
    )
    print("👂 Alenie przerszło przez ten kod...")
    for msg in consumer:
        print(f"Odebrano wiadomość: {msg.value}")
        messages.append(msg.value)

@app.route("/")
def home():
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
    <p><a href='/bikes'>🔗 Zobacz jako JSON</a></p>
    """
    return render_template_string(html_template, messages=list(messages))

@app.route("/bikes")
def get_bikes():
    return jsonify(list(messages))

if __name__ == "__main__":
    Thread(target=consume, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
