import sys
import requests
import random
import matplotlib.pyplot as plt
import io
from PIL import Image


class CityGuessingGame:
    def __init__(self, cities):
        self.cities = cities
        self.geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        self.api_key = input("Введите ваш API-ключ: ")

    def get_city_coordinates(self, city):
        geocoder_params = {
            "apikey": self.api_key,
            "geocode": city,
            "format": "json"
        }
        try:
            response = requests.get(self.geocoder_api_server, params=geocoder_params)
            response.raise_for_status()
            json_response = response.json()
            coordinates_str = \
            json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
            longitude, latitude = coordinates_str.split()
            return f"{longitude},{latitude}"

        except Exception as e:
            print(f"Ошибка получения координат для {city}: {e}")
            return None

    def get_map_image(self, coordinates, zoom=12):
        map_params = {
            "ll": coordinates,
            "z": zoom,
            "l": "map",
            "size": "650,450"
        }

        map_api_server = "https://static-maps.yandex.ru/1.x/"
        try:
            response = requests.get(map_api_server, params=map_params)
            response.raise_for_status()
            if response.status_code == 200:
                return Image.open(io.BytesIO(response.content))
            else:
                print(f"Ошибка получения карты: статус {response.status_code}")
                return None

        except Exception as e:
            print(f"Ошибка получения карты: {e}")
            return None

    def prepare_game_round(self):
        city = random.choice(self.cities)
        coordinates = self.get_city_coordinates(city)

        if coordinates:
            map_image = self.get_map_image(coordinates)
            if map_image:
                return {
                    "city": city,
                    "map_image": map_image
                }
        return None

    def play_game(self, num_rounds=5):
        score = 0
        for round_num in range(1, num_rounds + 1):
            print(f"\nРаунд {round_num}")
            game_round = self.prepare_game_round()
            if game_round:
                plt.figure(figsize=(10, 7))
                plt.imshow(game_round['map_image'])
                plt.axis('off')
                plt.title(f"Угадай город - Раунд {round_num}")
                plt.show()
                guess = input("Ваше предположение о городе: ")
                if guess.lower() == game_round['city'].lower():
                    print("Правильно! Отлично!")
                    score += 1
                else:
                    print(f"Неверно! Это был город {game_round['city']}")
        print(f"\nИгра завершена! Ваш счет: {score} из {num_rounds}")


def main():
    cities = [
        "Москва", "Санкт-Петербург", "Новосибирск",
        "Екатеринбург", "Казань", "Нижний Новгород"
    ]
    game = CityGuessingGame(cities)
    game.play_game()


if __name__ == "__main__":
    main()
