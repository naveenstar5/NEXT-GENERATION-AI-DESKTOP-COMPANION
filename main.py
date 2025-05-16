import pyttsx3
import speech_recognition as sr
import keyboard
import os
import subprocess as sp
from decouple import config
from datetime import datetime
import webbrowser
import imdb    #film info
import wolframalpha
import time

import pyautogui
from conv import random_text
from random import choice
from online import find_my_ip,search_on_google,search_on_wikipedia,youtube,send_email,get_news,weather_forecast


# Initialize the TTS engine
engine = pyttsx3.init('sapi5')
engine.setProperty('volume', 1.0)  # Corrected the volume to 1.0
engine.setProperty('rate', 210)  #reduce speed of jarvis)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # 1- female voice, 0- male voice

# Load user and bot names from environment variables
USER = config('USER')
HOSTNAME = config('BOT')

def speak(text):
    engine.say(text)
    engine.runAndWait()  # It will wait for user input

def greet_me():
    hour = datetime.now().hour
    if (hour >= 6) and (hour < 12):
        speak(f"Good Morning {USER}")
    elif (hour >= 12) and (hour <= 16):  # According to time, it greets us
        speak(f"Good afternoon {USER}")
    elif (hour >= 16) and (hour < 19):
        speak(f"Good evening {USER}")
    speak(f"I am {HOSTNAME}. How may I assist you? {USER}")
# Listening state control
listening = False

def start_listening():
    global listening
    listening = True
    print("Started listening")

def pause_listening():
    global listening
    listening = False
    print("Paused listening")

# Register hotkeys for controlling the listening state
keyboard.add_hotkey('ctrl+alt+k', start_listening)
keyboard.add_hotkey('ctrl+alt+p', pause_listening)

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=7)
        except sr.WaitTimeoutError:
            print("[DEBUG] Listening timed out.")
            return None

    try:
        print("Recognizing....")
        queri = r.recognize_google(audio, language='en-in')
        print(f"[DEBUG] Recognized voice: {queri}")
        return queri
    except sr.UnknownValueError:
        print("[DEBUG] Could not understand audio.")
        return None
    except sr.RequestError as e:
        print(f"[DEBUG] Could not request results; {e}")
        return None



if __name__ == '__main__':
    greet_me()
    while True:
        if listening:
            spoken = take_command()
            if not spoken:
                print("[DEBUG] Nothing heard. Skipping...")
                continue

            query = spoken.lower()
            # Fix: changed 'query' to 'queri'
            if "how are you" in query:
                speak("I am absolutely fine sir. What about you?")

            elif "open command prompt" in query:
                speak("Opening command prompt")
                os.system('start cmd')

            elif "open camera" in query:
                speak("Opening camera")
                sp.run('start microsoft.windows.camera:', shell=True)

            elif "ip address" in query:
                ip_address = find_my_ip()
                speak(
                    f"your ip address is {ip_address}"
                )
                print(f"your Ip address is {ip_address}")

            elif "youtube" in query:
                speak("What do you want to play on youtube?")
                video = take_command().lower()
                youtube(video)

            elif "open google" in query:
                speak(f"What do you want to search on google {USER}")
                search_on_google(query)




            elif "wikipedia" in query:
                speak("What do you want to search on Wikipedia?")
                search = take_command()
                if not search:
                    speak("I didn't catch that. Please try again.")
                    continue
                print(f"[DEBUG] Final search term: {search}")
                results = search_on_wikipedia(search)
                if results:
                    speak("According to Wikipedia...")
                    speak(results)
                    print(results)
                else:
                    speak("Sorry, I couldn't find anything useful.")

            elif "send an email" in query:
                speak("On what email address do you want to send sir?. Please enter in the terminal")
                receiver_add = input("Email address:")
                speak("What should be the subject?")
                subject = take_command().capitalize()
                speak("What is the message?")
                message = take_command().capitalize()
                if send_email(receiver_add,subject,message):
                    speak("I have sent the email")
                    print("I have sent the email")
                else:
                    speak("something went wrong")

            elif "give me news" in query:
                speak(f"I am reading out th latest headlines of today")
                speak(get_news())
                speak("I am printing it on screen")
                print(*get_news(),sep='\n')

            elif "weather" in query:
                ip_address = find_my_ip()
                speak("Tell me name of your city  ")
                city = input("Enter name of your city: ")
                speak(f"Getting weather report of your city: {city}")
                weather,temp,feels_like = weather_forecast(city)
                speak(f"The current temperature is {temp},but it feels like {feels_like}")
                speak(f"Also the weather report talks about {weather}")
                speak("I am printing weather info on screen")
                print(f"Description:{weather}\nTemperature:{temp}\nFeels like: {feels_like}")






            elif "movie" in query:
                movies_db = imdb.IMDb()
                speak("Please tell me the movie name:")
                text = take_command()
                if text:  # Ensure text is not None or empty
                    text = str(text)  # Force it to be a string
                    print(f"[DEBUG] Searching for movie: {text}")  # For debugging
                    movies = movies_db.search_movie(text)
                    speak(f"Searching for {text}")
                    speak("I found these:")
                    if movies:
                        for movie in movies:
                            title = movie.get("title", "Title not available")
                            # Fetch full movie details to get the year
                            movie_info = movies_db.get_movie(movie.getID())
                            # Get the year from the full movie data
                            year = movie_info.get("year", "Year not available")
                            if year != "Year not available":
                                year_text = f"({year})"
                            else:
                                year_text = "Year not available"
                            speak(f"{title} {year_text}")  # Speak the title and year (if available)
                            rating = movie_info.get("rating", "Rating not available")
                            cast = movie_info.get("cast", [])
                            # Extract actor names from the cast list
                            actor_names = [actor["name"] for actor in cast[:5]] if cast else ["Cast not available"]
                            plot = movie_info.get('plot outline', 'Plot summary not available.')
                            speak(
                                f"{title} has IMDB ratings of {rating}. It has a cast of {', '.join(actor_names)}. The plot summary of the movie is: {plot}")
                            print(
                                f"{title} was released in {year_text}, has IMDB ratings of {rating}. It has a cast of {', '.join(actor_names)}. The plot summary of the movie is: {plot}")
                    else:
                        speak("Sorry, no results found.")
                else:
                    speak("I couldn't understand the movie name. Please try again.")


            elif "calculate" in query:
                app_id = "67V2EG-KXLXKGWTYV"
                client = wolframalpha.Client(app_id)
                ind = query.lower().split().index("calculate")
                text = query.split()[ind + 1:]
                result = client.query(" ".join(text))
                try:
                    ans = next(result.results).text
                    speak("The answer is " + ans)
                    print("The answer is "+ ans)
                except StopIteration:
                    speak("I couldn't find that . Please try again")

            elif "what is" in query or 'who is' in query or 'which is' in query:
                app_id = "67V2EG-KXLXKGWTYV"
                client = wolframalpha.Client(app_id)
                try:
                    ind = query.lower().index('what is') if 'what is' in query.lower() else \
                        query.lower().index('what is') if 'who is' in query.lower() else \
                        query.lower().index('what is') if 'which is' in query.lower() else None

                    if ind is not None:
                        text = query.split()[ind+2:]
                        result = client.query(" ".join(text))
                        ans = next(result.results).text
                        speak("The answer is " + ans)
                        print("The answer is" + ans)
                    else:
                        speak("I could not find that")

                except StopIteration:
                    speak("I couldn't find that .please try again")

            elif "subscribe" in query:
                speak("Everyone who are watching this video, Please subscribe for more amazing content")
                speak("Firstly go to youtube")
                webbrowser.open("https:/www.youtube.com/")
                speak("click on the search bar")
                pyautogui.moveTo(806,125,1)
                pyautogui.click(x=806,y=125,clicks =1,interval=0,button='left')
                pyautogui.typewrite("Error by night",0.1)
                time.sleep(1)
                speak("press enter")
                pyautogui.press('enter')
                pyautogui.moveTo(971,314,1)
                speak("Here you see our channel")
                pyautogui.moveTo(1638,314,1)
                speak("Click here to subscribe our channel")
                pyautogui.click(x=1688,y=314,clicks=1,interval=0,button='left')
                speak("And also Don't forget to press the bell icon")
                pyautogui.moveTo(1750,314,1)
                pyautogui.click(x=1750,y=314,clicks=1,interval=0,button='left')
                speak("turn on all notifications")
                pyautogui.click(x=1750,y=320,clicks=1,interval=0,button='left')