import requests
import time
import json
from kafka import KafkaProducer

#Dane o rowerach w seattle
#BIKE_STATUS_URL_SEATTLE = "https://mds.bird.co/gbfs/v2/public/seattle-washington/free_bike_status.json"
#BIKE_STATUS_URL_TEMPE = "https://mds.bird.co/gbfs/tempe/free_bike_status.json"

CITY_FEEDS = {
    "Seattle": "https://mds.bird.co/gbfs/v2/public/seattle-washington/free_bike_status.json",
    "Tempe": "https://mds.bird.co/gbfs/tempe/free_bike_status.json"
}

producer = KafkaProducer(
    bootstrap_servers="kafka:9092",  # nazwa usługi z docker-compose
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def fetch_bike_data(feed_url):
    res = requests.get(feed_url)
    res.raise_for_status()
    data = res.json()
    return data.get('data', {}).get('bikes', [])

def print_bikes(bikes):
    print(f"\n\n Znaleziono {len(bikes)} dostępnych rowerów.\n Wyświetlanie 5 pierwszych pozycji \n")
    for bike in bikes[:5]:  # Wyświetl pierwsze 5 rowerów
        print(f" - ID: {bike['bike_id']}, Lat: {bike['lat']}, Lon: {bike['lon']}")

def main():
    print("🚲 Publisher uruchomiony – pobieranie danych rowerów z Seattle...\n")
    while True:
            for city, url in CITY_FEEDS.items():
                try:
                    bikes = fetch_bike_data(url)
                    print(f"📍 {city} → {len(bikes)} rowerów")

                    for bike in bikes[:5]:  # wysyłamy tylko pierwsze 5 dla testów
                        message = {
                            "city": city,
                            "bike_id": bike.get("bike_id"),
                            "lat": bike.get("lat"),
                            "lon": bike.get("lon")
                        }
                        producer.send("rowery", message)
                        print(f"➡️  Wysłano do Kafka: {message}")

                except Exception as e:
                    print(f"❌ Błąd dla {city}: {e}")

            time.sleep(10)

if __name__ == "__main__":
    main()