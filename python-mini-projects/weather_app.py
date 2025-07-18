import requests
import json

def get_weather(city):
    api_key = "YOUR_API_KEY"  # Replace with your OpenWeatherMap API key
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    complete_url = f"{base_url}appid={api_key}&q={city}"

    try:
        response = requests.get(complete_url)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        weather_data = json.loads(response.text)

        if weather_data["cod"] != 200:
            return f"Error: {weather_data['message']}"

        main = weather_data["main"]
        temperature = main["temp"] - 273.15  # Convert Kelvin to Celsius
        humidity = main["humidity"]
        description = weather_data["weather"][0]["description"]

        return f"Temperature in {city}: {temperature:.2f}°C\nHumidity: {humidity}%\nCondition: {description}"

    except requests.exceptions.RequestException as e:
        return f"Error fetching weather data: {e}"
    except KeyError as e:
        return f"Error parsing weather data: {e}"


if __name__ == "__main__":
    city = input("Enter city name: ")
    weather_info = get_weather(city)
    print(weather_info)

