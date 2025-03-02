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
        self.api_key = "8013b162-6b42-4997-9691-77b7074026e0"

    def get_city_coordinates(self, city):
        geocoder_params = {
            "apikey": self.api_key,
            "geocode": city,
            "format": "json",
            "results": 1
        }
        response = requests.get(self.geocoder_api_server, params=geocoder_params)

        if not response:
            print(f"Ошибка получения координат для {city}")
            return None

        try:
            json_response = response.json()
            coordinates = json_response["response"]["GeoObjectCollection"][("feature" "Member")][0]["GeoObject"]["Point"]["pos"]
            return coordinates
        except (KeyError, IndexError):
            print(f"Не удалось извлечь координаты для {city}")
            return None

    def get_map_image(self, coordinates, zoom=14):
        map_params = {
            "ll": coordinates,
            "z": zoom,
            "size": "650,450",
            "l": "map",
            "apikey": self.api_key
        }

        map_api_server = "http://static-maps.yandex.ru/1.x/"
        try:
            response = requests.get(map_api_server, params=map_params)
            if response.status_code == 200:
                return Image.open(io.BytesIO(response.content))
            else:
                print("Не удалось получить изображение карты")
                return None

        except Exception as e:
            print(f"Ошибка получения карты: {e}")
            return None

    def prepare_game_round(self):
        city = random.choice(self.cities)
        coordinates = self.get_city_coordinates(city)

        if not coordinates:
            return None

        map_image = self.get_map_image(coordinates)
        return {
            "city": city,
            "map_image": map_image
        }

    def play_game(self, num_rounds=5):
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
                else:
                    print(f"Неверно! Это был город {game_round['city']}")


def main():
    cities = [
        "Москва", "Санкт-Петербург", "Новосибирск",
        "Екатеринбург", "Казань", "Нижний Новгород"
    ]
    game = CityGuessingGame(cities)
    game.play_game()


if __name__ == "__main__":
    main()
