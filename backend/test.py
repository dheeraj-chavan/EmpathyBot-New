import os
import sys
import requests
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from textblob import TextBlob
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

# Download the VADER Lexicon for Sentiment Analysis
nltk.download("vader_lexicon")

app = Flask(__name__)
CORS(app)

# Secret Key for Session Handling
app.secret_key = "super_secret_key"

# Groq API Key (Replace with your API key)
GROQ_API_KEY = "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"

# Groq API Endpoint
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Initialize Sentiment Analyzer
sia = SentimentIntensityAnalyzer()

SYSTEM_INSTRUCTIONS = """
You are EmpathyBot, an AI chatbot designed to be empathetic, intelligent, and engaging.
Your responsibilities:
1. Answer factual questions correctly.
2. Solve math problems accurately.
3. Provide emotional support tailored to user needs.
4. Recognize key relationships in the user's life and personalize responses accordingly.
5. Offer motivational quotes, jokes, and guidance when appropriate.
6. Remember emotionally significant experiences and provide relevant support in future conversations.
7. Dynamically analyze emotions in user messages to ensure deeper understanding.
8. If the user mentions a close relationship (e.g., father, mother, brother, best friend), adjust responses to match that personality.
"""

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "EmpathyBot Backend (Groq API) is Running!"})

def analyze_emotions(user_message):
    """Detects emotional tone in the message using sentiment analysis"""
    blob = TextBlob(user_message)
    sentiment_score = sia.polarity_scores(user_message)

    detected_emotions = []

    if sentiment_score["compound"] < -0.4:  # Strong negative emotions
        detected_emotions.append("sadness")
    elif sentiment_score["compound"] > 0.4:  # Strong positive emotions
        detected_emotions.append("happiness")

    if "anxious" in user_message or "worried" in user_message:
        detected_emotions.append("anxiety")
    if "depressed" in user_message or "hopeless" in user_message:
        detected_emotions.append("depression")
    if "breakup" in user_message or "heartbroken" in user_message:
        detected_emotions.append("heartbreak")
    if "lost my job" in user_message or "fired" in user_message:
        detected_emotions.append("job loss")

    return detected_emotions

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_message = data.get("message", "")

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Expanded relationships list
        relationships = {
            "mom": "mother",
            "mother": "mother",
            "dad": "father",
            "father": "father",
            "brother": "elder brother",
            "big brother": "elder brother",
            "sister": "elder sister",
            "big sister": "elder sister",
            "best friend": "best friend",
            "teacher": "teacher",
            "therapist": "therapist",
            "mentor": "mentor",
            "uncle": "uncle",
            "aunt": "aunt",
            "grandfather": "grandfather",
            "grandmother": "grandmother",
            "cousin": "cousin"
        }

        # Check for relationship keywords and store in session
        for key, value in relationships.items():
            if key in user_message.lower():
                session["preferred_person"] = value
        
        # Adjust bot personality based on stored preference
        if "preferred_person" in session:
            personality_context = f"User prefers to talk to their {session['preferred_person']} about important matters. Adjust your responses to reflect a tone similar to a {session['preferred_person']}."
        else:
            personality_context = "User has not mentioned a preferred relationship yet. Provide a general empathetic response."

        # Analyze emotions dynamically
        detected_emotions = analyze_emotions(user_message)

        if detected_emotions:
            if "emotional_memory" not in session:
                session["emotional_memory"] = []
            session["emotional_memory"].extend(detected_emotions)
            session["emotional_memory"] = list(set(session["emotional_memory"]))  # Remove duplicates

        # Adjust for emotional memory
        if "emotional_memory" in session and session["emotional_memory"]:
            emotional_context = f"The user has expressed emotions like {', '.join(session['emotional_memory'])} in past conversations. Offer responses that acknowledge and provide support for these emotions."
        else:
            emotional_context = "User has not mentioned any emotionally significant events yet. Provide a supportive and neutral response."

        # Groq API request payload
        payload = {
            "model": "llama-3.3-70b-versatile",  # More updated and powerful model
            "messages": [
                {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                {"role": "system", "content": personality_context},
                {"role": "system", "content": emotional_context},
                {"role": "user", "content": user_message},
            ],
            "max_tokens": 120,
            "temperature": 0.7,
            "top_p": 0.9
        }

        # Headers
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        # Send request to Groq API
        response = requests.post(GROQ_API_URL, json=payload, headers=headers)

        # Convert response to JSON
        response_json = response.json()

        # Check if 'choices' exists in response
        if "choices" not in response_json:
            return jsonify({"error": "Invalid response from API", "details": response_json}), 500

        # Extract AI response
        bot_response = response_json["choices"][0]["message"]["content"].strip()

        return jsonify({"response": bot_response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)