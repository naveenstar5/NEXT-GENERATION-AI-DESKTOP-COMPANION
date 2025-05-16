
 import requests
import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError
import pywhatkit as kit #for google,youtube and accesing online
from email.message import EmailMessage
import smtplib
from decouple import config

EMAIL = 
PASSWORD = 



def find_my_ip():
    response = requests.get('https://api.ipify.org?format=json')
    ip_address = response.json()  # Convert the response to JSON
    return ip_address["ip"]





def search_on_wikipedia(query):
    try:
        print(f"[DEBUG] Original query: {query}")
        search_results = wikipedia.search(query)

        print(f"[DEBUG] Search results: {search_results}")
        if not search_results:
            return "Sorry, I couldn't find anything matching your query on Wikipedia."

        best_match = search_results[0]
        print(f"[DEBUG] Best match: {best_match}")

        page = wikipedia.page(best_match, auto_suggest=False)
        print(f"[DEBUG] Page title: {page.title}")

        summary = wikipedia.summary(page.title, sentences=2)
        return summary

    except DisambiguationError as e:
        print(f"[DEBUG] DisambiguationError: {e}")
        return f"Your search was too broad. Did you mean: {', '.join(e.options[:3])}?"
    except PageError as e:
        print(f"[DEBUG] PageError: {e}")
        return "Sorry, that page does not exist on Wikipedia."
    except Exception as e:
        print(f"[DEBUG] Unknown Error: {e}")
        return f"An error occurred: {str(e)}"




def search_on_google(query):
    kit.search(query)

def youtube(video):
    kit.playonyt(video)

def send_email(receiver_add,subject,message):
    try:
        email = EmailMessage()
        email['To'] = receiver_add
        email['subject'] = subject
        email['From'] = EMAIL

        email.set_content(message)
        s = smtplib.SMTP("smtp.gmail.com",587)
        s.starttls()
        s.login(EMAIL,PASSWORD)
        s.send_message(email)
        s.close()
        return True

    except Exception as e:
        print(e)
        return False

def get_news():
    news_headline = []
    result = requests.get(f"https://newsapi.org/v2/top-headlines?country=in&category=business&apiKey=202bf109c2794a6fa465b5864a8877a6").json()
    articles = result["articles"]
    for article in articles:
        news_headline.append(article["title"])
    return news_headline[:6]


def weather_forecast(city):
    res = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid=895431ff85b25266dc6d7cd882d0414d").json()
    weather = res["weather"][0]["main"]
    temp_kelvin = res["main"]["temp"]
    feels_like_kelvin = res["main"]["feels_like"]

    # Convert Kelvin to Celsius
    temp_celsius = temp_kelvin - 273.15
    feels_like_celsius = feels_like_kelvin - 273.15

    return weather, f"{temp_celsius:.2f}°C", f"{feels_like_celsius:.2f}°C"