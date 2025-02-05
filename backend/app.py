import os
import sys
import requests
import bcrypt
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from pymongo import MongoClient
from textblob import TextBlob
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
from datetime import datetime
from load_env import MONGO_URI, GROQ_API, APP_SECRETE_KEY

# Download the VADER Lexicon for Sentiment Analysis
nltk.download("vader_lexicon")

app = Flask(__name__)
CORS(app)

# Secret Key for Session Handling
app.secret_key = APP_SECRETE_KEY

# MongoDB Connection
client = MongoClient(MONGO_URI)
db = client["chatbot_db"]
users_collection = db["users"]

# Groq API Key and Endpoint
GROQ_API_KEY = GROQ_API
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Initialize Sentiment Analyzer
sia = SentimentIntensityAnalyzer()

SYSTEM_INSTRUCTIONS = """
You are EmpathyBot, an AI chatbot designed to be empathetic, intelligent, and engaging. and make it short and sweet in only max 100 words and keep the tone casual and use slang
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

def analyze_emotions(user_message):
    sentiment_score = sia.polarity_scores(user_message)
    detected_emotions = set()

    if sentiment_score["compound"] < -0.4:
        detected_emotions.add("sadness")
    elif sentiment_score["compound"] > 0.4:
        detected_emotions.add("happiness")

    keywords = {
        "anxious": "anxiety",
        "worried": "anxiety",
        "depressed": "depression",
        "hopeless": "depression",
        "breakup": "heartbreak",
        "heartbroken": "heartbreak",
        "lost my job": "job loss",
        "fired": "job loss"
    }

    for word, emotion in keywords.items():
        if word in user_message.lower():
            detected_emotions.add(emotion)

    return list(detected_emotions)

@app.route("/", methods=["GET"])
def ping():
    return jsonify({"message": "Server is running"})

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    user_name = data.get("user_name").lower()
    user_password = data.get("user_password")

    if not user_name or not user_password:
        return jsonify({"error": "Username and password are required"}), 400

    if users_collection.find_one({"user_name": user_name}):
        return jsonify({"error": "Username already exists"}), 400

    hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt())
    user = {
        "user_name": user_name,
        "user_password": hashed_password,
        "chat_history": []  # Initialize empty chat history array
    }
    users_collection.insert_one(user)
    return jsonify({"message": "User registered successfully"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user_name = data.get("user_name")
    user_password = data.get("user_password")

    user = users_collection.find_one({"user_name": user_name})
    if not user or not bcrypt.checkpw(user_password.encode('utf-8'), user["user_password"]):
        return jsonify({"error": "Invalid username or password"}), 400
    
    session["user_id"] = str(user["_id"])
    return jsonify({"message": "Login successful", "user_id": str(user["_id"])}), 200

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_message = data.get("message", "")
        user_id = data.get("user_id", "")
        chat_id = data.get("chat_id", "")

        if not user_message or not user_id or not chat_id:
            return jsonify({"error": "Missing required fields"}), 400

        user = users_collection.find_one({"user_name": user_id})
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get emotional analysis
        emotions = analyze_emotions(user_message)

        # Find the chat history for this chat_id
        chat_found = False
        recent_messages = []
        if "chat_history" in user:
            for chat in user["chat_history"]:
                if chat.get("chat_id") == chat_id:
                    chat_found = True
                    if "messages" in chat:
                        recent_messages = chat["messages"][-10:]  # Get last 10 messages
                    break

        # Prepare conversation history for the API
        conversation_history = [{"role": "system", "content": SYSTEM_INSTRUCTIONS}]
        for message in recent_messages:
            conversation_history.append(message)
        conversation_history.append({"role": "user", "content": user_message})

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": conversation_history,
            "max_tokens": 120,
            "temperature": 0.7,
            "top_p": 0.9
        }

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(GROQ_API_URL, json=payload, headers=headers)
        response_json = response.json()

        if "choices" not in response_json:
            return jsonify({"error": "Invalid response from API", "details": response_json}), 500

        bot_response = response_json["choices"][0]["message"]["content"].strip()

        # Prepare new messages
        new_messages = [
            {"role": "user", "content": user_message, "timestamp": datetime.utcnow().isoformat()},
            {"role": "assistant", "content": bot_response, "timestamp": datetime.utcnow().isoformat()}
        ]

        if chat_found:
            # Update existing chat
            users_collection.update_one(
                {
                    "user_name": user_id,
                    "chat_history.chat_id": chat_id
                },
                {
                    "$push": {
                        "chat_history.$.messages": {
                            "$each": new_messages
                        }
                    }
                }
            )
        else:
            # Create new chat
            users_collection.update_one(
                {"user_name": user_id},
                {
                    "$push": {
                        "chat_history": {
                            "chat_id": chat_id,
                            "created_at": datetime.utcnow().isoformat(),
                            "messages": new_messages
                        }
                    }
                }
            )

        return jsonify({
            "response": bot_response,
            "emotions": emotions
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/chat_history", methods=["GET"])
def get_chat_history():
    user_id = request.args.get("user_id")
    chat_id = request.args.get("chat_id")
    
    if not user_id or not chat_id:
        return jsonify({"error": "Missing required parameters"}), 400

    user = users_collection.find_one({"user_name": user_id})
    if not user:
        return jsonify({"error": "User not found"}), 404

    chat_history = None
    if "chat_history" in user:
        for chat in user["chat_history"]:
            if chat.get("chat_id") == chat_id:
                chat_history = chat
                break

    if not chat_history:
        return jsonify({"messages": []})

    return jsonify({"messages": chat_history.get("messages", [])})

if __name__ == "__main__":
    app.run(debug=True)