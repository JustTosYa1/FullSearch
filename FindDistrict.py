import sys
import requests


def get_district_info(address):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": "8013b162-6b42-4997-9691-77b7074026e0",
        "geocode": address,
        "format": "json"
    }

    response = requests.get(geocoder_api_server, params=geocoder_params)
    if not response:
        print("Ошибка получения координат")
        return None
    json_response = response.json()

    try:
        coordinates = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
        district_params = {
            "apikey": "8013b162-6b42-4997-9691-77b7074026e0",
            "geocode": coordinates,
            "format": "json",
            "kind": "district",
            "results": 1
        }
        district_response = requests.get(geocoder_api_server, params=district_params)

        if not district_response:
            print("Ошибка получения информации о районе")
            return None

        district_json = district_response.json()
        district_info = district_json["response"]["GeoObjectCollection"]["featureMember"]

        if district_info:
            district = district_info[0]["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["text"]
            return district
        else:
            return "Район не определен"

    except (KeyError, IndexError):
        print("Не удалось получить информацию о районе")
        return None


def main():
    if len(sys.argv) < 2:
        print("Введите корректный адрес!")
        return

    address = " ".join(sys.argv[1:])
    district = get_district_info(address)

    if district:
        print(f"Адрес: {address}")
        print(f"Район: {district}")


if __name__ == "__main__":
    main()
