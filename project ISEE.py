import cv2
import face_recognition
import pytesseract
import pyttsx3
import os
import speech_recognition as sr
import tkinter as tk
from PIL import Image, ImageTk

# Function to get the name from the file path
def get_name_from_path(file_path):
    return os.path.splitext(os.path.basename(file_path))[0]

# Function to use text-to-speech
def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Function to recognize speech
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        query = recognizer.recognize_google(audio).lower()
        print("User: ", query)
        return query
    except sr.UnknownValueError:
        return ""

# Function to interact with the virtual assistant based on user queries
def virtual_assistant(known_faces, known_names):
    speak_text("Hello! Initializing webcam for face recognition.")
    print("IRIS: Hello! Initializing webcam for face recognition.")

    # Load the video capture
    cap = cv2.VideoCapture(0)  # Use 0 for default camera, or provide the path to a video file

    while True:
        # Read a frame from the video capture
        ret, frame = cap.read()

        # Find all face locations in the frame
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        # Loop through each face found in the frame
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Check if the face matches any of the known faces
            matches = face_recognition.compare_faces(known_faces, face_encoding)

            name = "Unknown"

            # If a match is found, use the name associated with the known face
            if True in matches:
                first_match_index = matches.index(True)
                name = known_names[first_match_index]

            # Draw a rectangle around the face and display the name
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

            # Speak the detected name
            speak_text("Detected: " + name)
            print("IRIS: Detected -", name)

        # Display the frame
        cv2.imshow('Face Recognition', frame)

        # Recognize speech to check for specific commands
        query = recognize_speech()
        if "stop iris" in query or "quit iris" in query:
            speak_text("Stopping face recognition. Goodbye!")
            print("IRIS: Stopping face recognition. Goodbye!")
            break
        elif "who am i seeing" in query or "who is in front of me" in query:
            speak_text("You are currently seeing: " + name)
            print("IRIS: You are currently seeing -", name)
        elif "add new face" in query:
            # Capture new face when the command is given
            new_face, new_name = capture_new_face(frame)
            known_faces.append(new_face)
            known_names.append(new_name)
            speak_text("New face has been captured and recognized.")
            print("IRIS: New face has been captured and recognized.")

    # Release the video capture and close the OpenCV window
    cap.release()
    cv2.destroyAllWindows()

# Function to capture a new face manually
def capture_new_face(frame):
    # Encode the captured face
    new_encoding = face_recognition.face_encodings(frame)[0]

    # Manually enter the name for the new face
    new_name = input("Enter the name for the new face: ")

    # Save the captured face image
    image_path = os.path.join("known_faces", f"{new_name}.jpg")
    cv2.imwrite(image_path, frame)

    return new_encoding, new_name

# Main loop for speech recognition and interaction
# (remaining part of your code remains unchanged)

# Specify the path to the folder containing face images
faces_directory = "known_faces"

# List of known faces and their corresponding names
known_faces = []
known_names = []

# Load known faces from images in the specified directory
for file_name in os.listdir(faces_directory):
    file_path = os.path.join(faces_directory, file_name)
    if os.path.isfile(file_path):
        image = face_recognition.load_image_file(file_path)
        encoding = face_recognition.face_encodings(image)[0]
        known_faces.append(encoding)
        known_names.append(get_name_from_path(file_path))

while True:
    query = recognize_speech()
    if "hey iris" in query or "hello iris" in query or "hi iris" in query:
        virtual_assistant(known_faces, known_names)
    elif "stop iris" in query or "quit iris" in query:
        speak_text("Goodbye!")
        print("IRIS: Goodbye!")
        break
