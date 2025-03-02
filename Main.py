import sys
import requests
from io import BytesIO
from PIL import Image
from map_scale import get_map_scale_params


def main():
    if len(sys.argv) < 2:  # Введение данных через терминал
        print("Введите корректный адрес!")
        return

    # Формат ввода данных - python main.py Город, ул. Название улицы, номер дома

    toponym_to_find = " ".join(sys.argv[1:])
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": "8013b162-6b42-4997-9691-77b7074026e0",
        "geocode": toponym_to_find,
        "format": "json"
    }
    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        print("Error fetching geocoder data")
        return

    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]

    toponym_coordinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_latitude = toponym_coordinates.split()
    lon_span, lat_span = get_map_scale_params(toponym)
    apikey = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"

    map_params = {
        "ll": f"{toponym_longitude},{toponym_latitude}",
        "spn": f"{lon_span},{lat_span}",
        "apikey": apikey,
        "pt": f"{toponym_longitude},{toponym_latitude},pm2rdm"
    }

    map_api_server = "https://static-maps.yandex.ru/v1"
    response = requests.get(map_api_server, params=map_params)

    with BytesIO(response.content) as im:
        opened_image = Image.open(im)
        opened_image.show()
        opened_image.save("map.png")


if __name__ == "__main__":
    main()
