import sys
import math
import requests
from io import BytesIO
from PIL import Image


def get_coordinates(address):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": "8013b162-6b42-4997-9691-77b7074026e0",
        "geocode": address,
        "format": "json"
    }
    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        print("Error fetching geocoder data")
        return None

    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]

    coordinates = toponym["Point"]["pos"]
    longitude, latitude = coordinates.split()

    return (longitude, latitude)


def find_pharmacies(longitude, latitude):
    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

    search_params = {
        "apikey": api_key,
        "text": "аптека",
        "lang": "ru_RU",
        "ll": f"{longitude},{latitude}",
        "type": "biz",
        "results": 10
    }

    response = requests.get(search_api_server, params=search_params)

    if not response:
        print("Error searching for pharmacies")
        return None

    json_response = response.json()

    if not json_response.get("features"):
        print("No pharmacies found")
        return None

    return json_response["features"]


def calculate_distance(coord1, coord2):
    lon1, lat1 = map(float, coord1)
    lon2, lat2 = map(float, coord2)

    R = 6371.0
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def determine_pharmacy_color(pharmacy):
    try:
        hours = pharmacy["properties"]["CompanyMetaData"]["Hours"]["Availability"]
        if hours == "24":
            return "pm2gnl"
        else:
            return "pm2dnl"
    except KeyError:
        return "pm2grm"


def generate_map(address_point, pharmacies):
    map_api_server = "https://static-maps.yandex.ru/v1"
    apikey = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"

    lon1, lat1 = map(float, address_point)
    pharmacy_coords = [
        (float(pharmacy["geometry"]["coordinates"][0]),
         float(pharmacy["geometry"]["coordinates"][1]))
        for pharmacy in pharmacies
    ]

    lons = [lon1] + [coord[0] for coord in pharmacy_coords]
    lats = [lat1] + [coord[1] for coord in pharmacy_coords]

    center_lon = sum(lons) / len(lons)
    center_lat = sum(lats) / len(lats)

    lon_span = max(abs(lon - center_lon) for lon in lons) * 2.5
    lat_span = max(abs(lat - center_lat) for lat in lats) * 2.5

    points = f"{lon1},{lat1},pm2rdm"
    for pharmacy in pharmacies:
        lon, lat = pharmacy["geometry"]["coordinates"]
        color = determine_pharmacy_color(pharmacy)
        points += f"~{lon},{lat},{color}"

    map_params = {
        "ll": f"{center_lon},{center_lat}",
        "spn": f"{lon_span},{lat_span}",
        "apikey": apikey,
        "pt": points
    }

    response = requests.get(map_api_server, params=map_params)

    with BytesIO(response.content) as im:
        opened_image = Image.open(im)
        opened_image.save("pharmacies_map.png")
        opened_image.show()


def main():
    if len(sys.argv) < 2:
        print("Введите корректный адрес!")
        return

    address = " ".join(sys.argv[1:])
    address_coords = get_coordinates(address)
    if not address_coords:
        return

    pharmacies = find_pharmacies(*address_coords)
    if not pharmacies:
        return

    print("Найденные аптеки:")
    for i, pharmacy in enumerate(pharmacies, 1):
        name = pharmacy["properties"]["CompanyMetaData"]["name"]
        address = pharmacy["properties"]["CompanyMetaData"]["address"]

        try:
            hours = pharmacy["properties"]["CompanyMetaData"]["Hours"]["text"]
        except KeyError:
            hours = "Время работы не указано"

        distance = calculate_distance(address_coords, pharmacy["geometry"]["coordinates"])

        print(f"\n{i}. Название: {name}")
        print(f"   Адрес: {address}")
        print(f"   Время работы: {hours}")
        print(f"   Расстояние: {distance:.2f} км")
    generate_map(address_coords, pharmacies)


if __name__ == "__main__":
    main()
