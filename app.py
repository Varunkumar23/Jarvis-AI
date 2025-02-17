from flask import Flask, request, jsonify
from flask_cors import CORS
import speech_recognition as sr
import google.generativeai as genai
import pyttsx3

# Configure Gemini API
genai.configure(api_key="AIzaSyAUbpmuyQt3wGrkY3p4fsaSIS5HMyXkO3c")
model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)
CORS(app)  # Enable frontend-backend communication

def system_voice(text):
    """Convert AI response to speech"""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def recognize_speech():
    """Recognize user speech input"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        try:
            print("Listening...")
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio)
            return text.lower()
        except sr.UnknownValueError:
            return "Sorry, I didn't catch that."
        except sr.RequestError:
            return "Speech Recognition service is unavailable."

def get_ai_response(user_input):
    """Get AI-generated response"""
    try:
        response = model.generate_content(user_input)
        return response.text
    except Exception as e:
        return f"Error processing request: {e}"

@app.route('/text', methods=['POST'])
def handle_text():
    """Handle text input from frontend"""
    data = request.json
    user_input = data.get("prompt", "")
    ai_response = get_ai_response(user_input)
    return jsonify({"response": ai_response})

@app.route('/voice', methods=['GET'])
def handle_voice():
    """Handle voice input from frontend"""
    user_input = recognize_speech()
    if not user_input or "sorry" in user_input.lower():
        return jsonify({"prompt": user_input, "response": "Please try again."})
    
    ai_response = get_ai_response(user_input)
    return jsonify({"prompt": user_input, "response": ai_response})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
