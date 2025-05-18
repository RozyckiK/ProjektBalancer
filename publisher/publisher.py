import requests
import time

#Dane o rowerach w seattle
BIKE_STATUS_URL_SEATTLE = "https://mds.bird.co/gbfs/v2/public/seattle-washington/free_bike_status.json"
BIKE_STATUS_URL_TEMPE = "https://mds.bird.co/gbfs/tempe/free_bike_status.json"

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
        try:
            #Pobieranie i wyświetlanie w konsoli wyników dla miasta SEATTLE
            bikes = fetch_bike_data(BIKE_STATUS_URL_SEATTLE)
            print_bikes(bikes)

            #Pobieranie i wyświetlanie w konsoli wyników dla Miasta Tempe
            bikes = fetch_bike_data(BIKE_STATUS_URL_TEMPE)
            print_bikes(bikes)


            print("\nCzekam 10 sekund...\n")
            time.sleep(10)
        except Exception as e:
            print(f"Błąd podczas pobierania danych: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()