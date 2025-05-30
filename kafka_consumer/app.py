import time
from threading import Thread
from collections import deque
from kafka import KafkaConsumer
from prometheus_client import start_http_server, Gauge

# --- metryki Prometheusa
rps_gauge        = Gauge('kafka_consumer_rps',           'Messages consumed per second')
avg_latency_gauge = Gauge('kafka_consumer_avg_latency_ms', 'Average end-to-end latency in ms (sliding window)')
max_latency_gauge = Gauge('kafka_consumer_max_latency_ms', 'Maximum end-to-end latency in ms (per second)')

# ustaw okno na ostatnie N sekund
WINDOW_SEC = 2
lat_window = deque()  # będzie trzymać (ts, latency_ms)

def run_http_server():
    start_http_server(8000)

Thread(target=run_http_server, daemon=True).start()

consumer = KafkaConsumer(
    'test-topic',
    bootstrap_servers=['kafka:9092'],
    group_id='my-group',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
)

msg_count = 0
rps_ts     = time.time()

while True:
    # pollujemy maks. 1s
    records = consumer.poll(timeout_ms=1000, max_records=100)
    now = time.time()
    for tp, msgs in records.items():
        for msg in msgs:
            now_ms  = now * 1000
            lat_ms  = now_ms - msg.timestamp
            # dorzucamy do okna
            if lat_ms < 0:
                lat_ms = 0.0
            lat_window.append((now, lat_ms))
            msg_count += 1

    # co sekundę liczymy RPS i uśrednioną latency z okna
    if now - rps_ts >= 1.0:
        # 1) RPS za ostatnią sekundę
        rps_gauge.set(msg_count)

        # 2) obliczamy tylko te wpisy z lat_window, które są młodsze niż WINDOW_SEC
        cutoff = now - WINDOW_SEC
        # usuń stare
        while lat_window and lat_window[0][0] < cutoff:
            lat_window.popleft()

        # wyciągnij same latency
        window_lats = [lat for ts, lat in lat_window]
        if window_lats:
            avg = sum(window_lats) / len(window_lats)
        else:
            avg = 0.0

        avg_latency_gauge.set(avg)

        # 3) max latency tylko w tej sekundzie (jak miałeś dotychczas)
        #    możesz tu też window-ować, ale zostawiłem per-second
        #    abyś nadal miał widok outlierów
        max_this_sec = max(window_lats) if window_lats else 0.0
        max_latency_gauge.set(max_this_sec)

        # reset licznika RPS
        msg_count = 0
        rps_ts     = now
