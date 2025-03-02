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


def find_nearest_pharmacy(longitude, latitude):
    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

    search_params = {
        "apikey": api_key,
        "text": "аптека",
        "lang": "ru_RU",
        "ll": f"{longitude},{latitude}",
        "type": "biz",
        "results": 1
    }

    response = requests.get(search_api_server, params=search_params)

    if not response:
        print("Error searching for pharmacies")
        return None

    json_response = response.json()

    if not json_response.get("features"):
        print("No pharmacies found")
        return None

    pharmacy = json_response["features"][0]
    return pharmacy


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


def generate_map(address_point, pharmacy_point):
    map_api_server = "https://static-maps.yandex.ru/v1"
    apikey = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"

    lon1, lat1 = map(float, address_point)
    lon2, lat2 = map(float, pharmacy_point)

    center_lon = (lon1 + lon2) / 2
    center_lat = (lat1 + lat2) / 2

    lon_span = abs(lon1 - lon2) * 1.5
    lat_span = abs(lat1 - lat2) * 1.5

    map_params = {
        "ll": f"{center_lon},{center_lat}",
        "spn": f"{lon_span},{lat_span}",
        "apikey": apikey,
        "pt": f"{lon1},{lat1},pm2rdm~{lon2},{lat2},pm2gnl"
    }

    response = requests.get(map_api_server, params=map_params)

    with BytesIO(response.content) as im:
        opened_image = Image.open(im)
        opened_image.save("pharmacy_map.png")
        opened_image.show()


def main():
    if len(sys.argv) < 2:
        print("Введите корректный адрес!")
        return

    address = " ".join(sys.argv[1:])
    address_coords = get_coordinates(address)
    if not address_coords:
        return

    pharmacy = find_nearest_pharmacy(*address_coords)
    if not pharmacy:
        return

    pharmacy_name = pharmacy["properties"]["CompanyMetaData"]["name"]
    pharmacy_address = pharmacy["properties"]["CompanyMetaData"]["address"]
    pharmacy_coords = pharmacy["geometry"]["coordinates"]

    distance = calculate_distance(address_coords, pharmacy_coords)

    print(f"Ближайшая аптека:")
    print(f"Название: {pharmacy_name}")
    print(f"Адрес: {pharmacy_address}")
    print(f"Расстояние: {distance:.2f} км")

    generate_map(address_coords, pharmacy_coords)


if __name__ == "__main__":
    main()
