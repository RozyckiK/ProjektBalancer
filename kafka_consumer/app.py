import time
from threading import Thread
from kafka import KafkaConsumer
from prometheus_client import start_http_server, Gauge

# --- metryki Prometheusa jako serie czasowe (line chart)
rps_gauge = Gauge('kafka_consumer_rps', 'Messages consumed per second')
avg_latency_gauge = Gauge('kafka_consumer_avg_latency_ms',
                          'Average end-to-end latency in ms per second')
max_latency_gauge = Gauge('kafka_consumer_max_latency_ms',
                          'Maximum end-to-end latency in ms per second')

def run_http_server():
    # expose /metrics podowi na porcie 8000
    start_http_server(8000)

Thread(target=run_http_server, daemon=True).start()

consumer = KafkaConsumer(
    'rowery',
    bootstrap_servers=['kafka:9092'],
    group_id='my-group',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
)

# liczniki do RPS i latencji
msg_count = 0
latencies = []
rps_ts = time.time()

while True:
    poll_start = time.time()
    records = consumer.poll(timeout_ms=1000, max_records=100)
    # nie mierzymy fetch latency w tej wersji

    for tp, msgs in records.items():
        for msg in msgs:
            now_ms = time.time() * 1000
            lat_ms = now_ms - msg.timestamp
            latencies.append(lat_ms)
            # tu normalna logika przetwarzania
            msg_count += 1

    # co sekundę oblicz RPS i statystyki latencji
    now = time.time()
    if now - rps_ts >= 1.0:
        # RPS
        rps_gauge.set(msg_count)

        # średnia i max latencja z ostatniej sekundy
        if latencies:
            avg = sum(latencies) / len(latencies)
            mx  = max(latencies)
        else:
            avg = 0
            mx  = 0

        avg_latency_gauge.set(avg)
        max_latency_gauge.set(mx)

        # zeruj liczniki i czas
        msg_count = 0
        latencies.clear()
        rps_ts = now
