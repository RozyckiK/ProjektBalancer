#!/usr/bin/env python3
import time, math, json, argparse
from kafka import KafkaProducer
from prometheus_client import start_http_server, Gauge

# --- Parsowanie argumentów ---
parser = argparse.ArgumentParser()
parser.add_argument("--pattern",    choices=["constant","ramp","sinusoidal","spike"], default="constant")
parser.add_argument("--min-rps",    type=float, default=10)
parser.add_argument("--max-rps",    type=float, default=500)
parser.add_argument("--duration",   type=int,   default=600,  help="całkowity czas testu w sekundach")
parser.add_argument("--step-time",  type=int,   default=30,   help="interwał dla rampy")
parser.add_argument("--bootstrap",  type=str,   default="kafka:9092")
parser.add_argument("--topic",      type=str,   default="test-topic")
parser.add_argument("--metrics-port", type=int, default=8000)
args = parser.parse_args()

# --- Mierniki Prometheusa ---
start_http_server(args.metrics_port)
g_rps    = Gauge("target_rps",   "Celowane RPS", [])
g_sent   = Gauge("sent_total",   "Wysłane wiadomości", [])

# --- Funkcja do obliczania RPS ---
def get_target_rps(elapsed):
    mn, mx = args.min_rps, args.max_rps
    if args.pattern == "constant":
        return mn
    if args.pattern == "ramp":
        steps = elapsed // args.step_time
        inc   = (mx-mn) / (args.duration/args.step_time)
        return min(mn + steps*inc, mx)
    if args.pattern == "sinusoidal":
        amp = (mx-mn)/2; mid=(mx+mn)/2
        return mid + amp*math.sin(2*math.pi*elapsed/(args.duration/2))
    if args.pattern == "spike":
        cycle = elapsed % 60
        return mn if cycle<30 else min(mx, mn*2)
    return mn

# --- Inicjalizacja producenta ---
producer = KafkaProducer(
    bootstrap_servers=[args.bootstrap],
    value_serializer=lambda x: json.dumps(x).encode("utf-8")
)

# --- Pętla główna ---
start = time.time()
count = 0
while True:
    elapsed = time.time() - start
    if elapsed > args.duration:
        break
    target = get_target_rps(elapsed)
    interval = 1.0/target if target>0 else 1.0
    # wysyłamy przykładową wiadomość
    producer.send(args.topic, {"ts": time.time(), "i": count})
    count += 1
    g_rps.set(target)
    g_sent.inc()
    time.sleep(interval)

producer.flush()