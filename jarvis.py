import time
import threading
import keyboard
import numpy as np
import sounddevice as sd
import speech_recognition as sr
import os
import pyautogui
import subprocess as sp
import webbrowser
import imdb
from kivy.uix import widget, image, label, boxlayout, textinput
from kivy import clock
from constants import SCREEN_HEIGHT, SCREEN_WIDTH, GEMINI_API_KEY
from utils import speak, youtube, search_on_google, search_on_wikipedia, send_email, get_news, weather_forecast, find_my_ip
from jarvis_button import JarvisButton
import google.generativeai as genai

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

class Jarvis(widget.Widget):
    def __init__(self, **kwargs):
        super(Jarvis, self).__init__(**kwargs)
        self.volume = 0
        self.volume_history = [0] * 7
        self.volume_history_size = 140

        self.min_size = .2 * SCREEN_WIDTH
        self.max_size = .7 * SCREEN_WIDTH

        self.add_widget(image.Image(source='static/border.eps.png', size=(1920, 1080)))
        self.circle = JarvisButton(size=(284.0, 284.0), background_normal='static/circle.png')
        self.circle.bind(on_press=self.start_recording)
        self.start_recording()
        self.add_widget(image.Image(source='static/jarvis.gif', size=(self.min_size, self.min_size), pos=(SCREEN_WIDTH / 2 - self.min_size / 2, SCREEN_HEIGHT / 2 - self.min_size / 2)))

        time_layout = boxlayout.BoxLayout(orientation='vertical', pos=(150, 900))
        self.time_label = label.Label(text='', font_size=24, markup=True, font_name='static/mw.ttf')
        time_layout.add_widget(self.time_label)
        self.add_widget(time_layout)

        self.title = label.Label(text='[b][color=3333ff]NOVA[/color][/b]', font_size=42, markup=True, font_name='static/dusri.ttf', pos=(920, 900))
        self.add_widget(self.title)

        self.subtitles_input = textinput.TextInput(
            text='Hey  Asraar!  I  am  your  personal  assistant',
            font_size=24,
            readonly=False,
            background_color=(0, 0, 0, 0),
            foreground_color=(1, 1, 1, 1),
            size_hint_y=None,
            height=80,
            pos=(720, 100),
            width=1200,
            font_name='static/teesri.otf',
        )
        self.add_widget(self.subtitles_input)

        self.vrh = label.Label(text='', font_size=30, markup=True, font_name='static/mw.ttf', pos=(1500, 500))
        self.vlh = label.Label(text='', font_size=30, markup=True, font_name='static/mw.ttf', pos=(400, 500))
        self.add_widget(self.vrh)
        self.add_widget(self.vlh)
        self.add_widget(self.circle)
        keyboard.add_hotkey('`', self.start_recording)

        clock.Clock.schedule_interval(self.update_time, 1)

    def take_command(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            r.pause_threshold = 1
            audio = r.listen(source)

        try:
            print("Recognizing....")
            queri = r.recognize_google(audio, language='en-in')
            return queri.lower()
        except Exception:
            speak("Sorry I couldn't understand. Can you please repeat that?")
            return 'None'

    def start_recording(self, *args):
        print("recording started")
        threading.Thread(target=self.run_speech_recognition).start()
        print("recording ended")

    def run_speech_recognition(self):
        print('before speech rec obj')
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            audio = r.listen(source)
            print("audio recorded")

        print("after speech rec obj")

        try:
            query = r.recognize_google(audio, language="en-in")
            print(f'Recognised: {query}')
            clock.Clock.schedule_once(lambda dt: setattr(self.subtitles_input, 'text', query))
            self.handle_jarvis_commands(query.lower())
            return query.lower()

        except sr.UnknownValueError:
            print("Google speech recognition could not understand audio")

        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

        return None

    def update_time(self, dt):
        current_time = time.strftime('TIME\n\t%H:%M:%S')
        self.time_label.text = f'[b][color=3333ff]{current_time}[/color][/b]'

    def update_circle(self, dt):
        try:
            self.size_value = int(np.mean(self.volume_history))
        except Exception as e:
            self.size_value = self.min_size
            print('Warning:', e)

        self.size_value = max(self.min_size, min(self.size_value, self.max_size))
        self.circle.size = (self.size_value, self.size_value)
        self.circle.pos = (SCREEN_WIDTH / 2 - self.circle.width / 2, SCREEN_HEIGHT / 2 - self.circle.height / 2)

    def update_volume(self, indata, frames, time, status):
        volume_norm = np.linalg.norm(indata) * 200
        self.volume = volume_norm
        self.volume_history.append(volume_norm)
        self.volume_history = self.volume_history[-self.volume_history_size:]

        history_text = '\n'.join([str(round(v, 7)) for v in self.volume_history[-7:]])
        self.vrh.text = f'[b][color=3344ff]{history_text}[/color][/b]'
        self.vlh.text = f'[b][color=3344ff]{history_text}[/color][/b]'

    def start_listening(self):
        self.stream = sd.InputStream(callback=self.update_volume)
        self.stream.start()

    def get_gemini_response(self, query):
        try:
            response = model.generate_content(query)
            return response.text
        except Exception as e:
            print(f"Error getting Gemini response: {e}")
            return "I'm sorry, I couldn't process that request."

    def handle_jarvis_commands(self, query):
        try:
            if "how are you" in query:
                speak("I am absolutely fine sir. What about you")

            elif "open command prompt" in query:
                speak("Opening command prompt")
                os.system('start cmd')

            elif "open camera" in query:
                speak("Opening camera sir")
                sp.run('start microsoft.windows.camera:', shell=True)

            elif "open notepad" in query:
                speak("Opening Notepad for you sir")
                notepad_path = "C:\\Windows\\notepad.exe"
                os.startfile(notepad_path)

            elif "youtube" in query:
                speak("What do you want to play on youtube sir?")
                video = self.take_command().lower()
                youtube(video)

            elif "search on google" in query:
                speak(f"What do you want to search on google")
                query = self.take_command().lower()
                search_on_google(query)

            elif "search on wikipedia" in query:
                speak("what do you want to search on wikipedia sir?")
                search = self.take_command().lower()
                results = search_on_wikipedia(search)
                speak(f"According to wikipedia,{results}")
                
            elif "send an email" in query:
                    speak("On what email address do you want to send sir?. Please enter in the terminal")
                    receiver_add = input("Email address:")
                    speak("What should be the subject sir?")
                    subject = self.take_command().capitalize()
                    speak("What is the message ?")
                    message = self.take_command().capitalize()
                    if send_email(receiver_add, subject, message):
                        speak("I have sent the email sir")
                        print("I have sent the email sir")
                    else:
                        speak("something went wrong Please check the error log")

            elif "tell me news" in query:
                speak(f"I am reading out the latest headline of today,sir")
                speak(get_news())

            elif 'weather' in query:
                speak("tell me the name of your city")
                city = input("Enter name of your city")
                speak(f"Getting weather report for your city {city}")
                weather, temp, feels_like = weather_forecast(city)
                speak(f"The current temperature is {temp}, but it feels like {feels_like}")
                speak(f"Also, the weather report talks about {weather}")
                print(f"Description: {weather}\nTemperature: {temp}\nFeels like: {feels_like}")

            else:
                gemini_response = self.get_gemini_response(query)
                gemini_response = gemini_response.replace("*", "")
                if gemini_response:
                    speak(gemini_response)
                    print(gemini_response)

        except Exception as e:
            print(e)