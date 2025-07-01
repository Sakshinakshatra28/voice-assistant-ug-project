import sqlite3
import os
import pygame
import speech_recognition as sr
import pyttsx3
import datetime
import pyjokes
import pywhatkit
import wikipedia
import webbrowser
import requests
import subprocess
import tkinter as tk
from threading import Thread

# Initialize text-to-speech engine
engine = pyttsx3.init()

def speak(text):
    """Convert text to speech and print it."""
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

# 🔹 Database Setup
def setup_database():
    """Create songs table if it doesn't exist."""
    conn = sqlite3.connect("assistant.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS songs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE,
                        path TEXT)''')
    conn.commit()
    conn.close()

def add_song(name, path):
    """Add a song to the database."""
    conn = sqlite3.connect("assistant.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO songs (name, path) VALUES (?, ?)", (name, path))
        conn.commit()
        print(f"Song '{name}' added successfully!")
    except sqlite3.IntegrityError:
        print(f"Song '{name}' already exists in the database.")
    conn.close()

# 🔹 Function to Play Songs from the Database
def play_song(song_name):
    conn = sqlite3.connect("assistant.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT path FROM songs WHERE name = ?", (song_name,))
    result = cursor.fetchone()
    
    if result:
        song_path = result[0]
        print(f"Playing '{song_name}' from: {song_path}")
        
        if os.path.exists(song_path):  # Check if the file exists
            pygame.mixer.init()
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
            speak(f"Now playing {song_name}")
        else:
            speak("Sorry, the song file does not exist.")
    else:
        speak(f"Sorry, I couldn't find {song_name} in the database.")

    conn.close()

# 🔹 Function to Get Weather
def get_weather(city):
    """Fetch weather information for a given city."""
    api_key = "your_openweathermap_api_key"  # Replace with your API key
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        if data["cod"] == 200:
            weather = data["weather"][0]["description"].capitalize()
            temp = data["main"]["temp"]
            speak(f"The weather in {city} is {weather} with a temperature of {temp} degrees Celsius.")
        else:
            speak("I couldn't fetch the weather information. Please check the city name.")
    except Exception as e:
        speak("There was an error retrieving the weather information.")
        print("Error:", e)

# 🔹 Function to Open Applications
def open_application(app_name):
    """Open an application based on user command."""
    app_paths = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "word": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
        "excel": "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE"
    }
    if app_name in app_paths:
        subprocess.Popen(app_paths[app_name])
        speak(f"Opening {app_name}")
    else:
        speak("I couldn't find that application.")

# 🔹 Function to Handle Commands

def play_song(song_name):
    """Retrieve and play the song from the database"""
    conn = sqlite3.connect("assistant.db")
    cursor = conn.cursor()
    
    # Check if the song exists
    cursor.execute("SELECT path FROM songs WHERE name LIKE ?", (f"%{song_name}%",))
    result = cursor.fetchone()
    
    conn.close()

    if result:
        song_path = result[0]
        speak(f"Playing {song_name}")
        os.startfile(song_path)  # Opens the file with the default media player
    else:
        speak(f"Sorry, I couldn't find {song_name} in the database.")

def handle_command(command):
    """Process and respond to user commands"""
    response = "I'm not sure how to help with that."
    
    if "your name" in command:
        response = "I'm Virtual Assistant."
    elif "how are you" in command:
        response = "I'm good."
    elif "joke" in command:
        response = pyjokes.get_joke()
    elif "search" in command:
        search_query = command.replace("search", "").strip()
        pywhatkit.search(search_query)
        response = f"Searching for {search_query} on Google."
    elif "youtube" in command or "play" in command:
        song_name = command.replace("play", "").replace("on youtube", "").strip()
        speak(f"Playing {song_name} on YouTube")
        pywhatkit.playonyt(song_name)
        return  # Stop further execution

    elif "time" in command:
        response = f"The time is {datetime.datetime.now().strftime('%I:%M %p')}"
    elif "weather" in command:
        city = command.replace("weather in", "").strip()
        get_weather(city)
        return
    elif "open" in command:
        app_name = command.replace("open", "").strip()
        open_application(app_name)
        return
    
    speak(response)

# 🔹 Assistant Triggered Only When Button is Clicked
def start_assistant():
    """Starts the assistant only when the button is clicked."""
    speak("Hi, I'm your assistant. How may I help you?")
    user_command = listen()
    if "exit" in user_command or "stop" in user_command:
        speak("Goodbye!")
    else:
        handle_command(user_command)

def listen():
    """Capture voice input from the user"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio).lower()
            print(f"You: {command}")
            return command
        except sr.UnknownValueError:
            return "Sorry, I didn't understand that."
        except sr.RequestError:
            return "Could not request results. Check your internet connection."
        except sr.WaitTimeoutError:
            return "No input received."

def on_button_click():
    """Runs the assistant ONCE on a separate thread."""
    Thread(target=start_assistant, daemon=True).start()

# 🔹 GUI Setup
root = tk.Tk()
root.title("Virtual Assistant")
root.geometry("400x300")
root.configure(bg="#282c34")

label = tk.Label(root, text="Click the button to start the assistant", fg="white", bg="#282c34", font=("Arial", 12))
label.pack(pady=20)

button = tk.Button(root, text="Start Assistant", command=on_button_click, font=("Arial", 14), bg="#61afef", fg="black")
button.pack(pady=10)

# 🔹 Setup the database
setup_database()
add_song("Shape of You", r"C:\Users\Sasikumar\Downloads\Ed Sheeran  Shape of You Official Music Video.mp3")

root.mainloop()
