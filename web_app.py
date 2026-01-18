from flask import Flask, render_template, jsonify, request
import datetime
import requests
import json
import os
import re
import random

app = Flask(__name__)

# Create data directory if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')

class WebARIA:
    def __init__(self):
        self.current_city = "Bangalore"
        self.weather_api_key = "e49769670c7f79929a39b0ae4222e114"
        self.news_api_key = "943a03257fdf4ff68cd90c151978c3bb"
    
    def process_command(self, command):
        """Process user command and return response"""
        command_lower = command.lower()
        
        # Extract city from command
        city_match = self.extract_city_from_command(command)
        if city_match:
            self.current_city = city_match
        
        # Process commands
        if any(word in command_lower for word in ["weather", "temperature", "forecast", "climate"]):
            weather_info = self.get_weather()
            return f"🌤️ **Weather in {self.current_city}:**\n{weather_info}"
        
        elif any(word in command_lower for word in ["news", "headlines", "updates"]):
            news_info = self.get_news()
            return f"📰 **Latest News:**\n{news_info}"
        
        elif "time" in command_lower:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            return f"⏰ The current time is **{current_time}**"
        
        elif "date" in command_lower:
            current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
            return f"📅 Today is **{current_date}**"
        
        elif any(word in command_lower for word in ["hello", "hi", "hey", "greetings"]):
            responses = [
                "Hello! I'm ARIA, your AI assistant. How can I help you today? 🌟",
                "Hi there! Ready to assist with weather, news, or any questions! 💫",
                "Greetings! I'm here to help. What would you like to know? ✨"
            ]
            return random.choice(responses)
        
        elif any(word in command_lower for word in ["thank", "thanks", "thank you"]):
            responses = [
                "You're most welcome! 😊",
                "My pleasure! Happy to help! 💫",
                "Always here for you! 🌟"
            ]
            return random.choice(responses)
        
        elif any(word in command_lower for word in ["reminder", "remind"]):
            if "set" in command_lower:
                return self.set_reminder(command)
            else:
                return self.show_reminders()
        
        elif any(word in command_lower for word in ["stop", "exit", "quit", "bye", "goodbye"]):
            return "Goodbye! Have a wonderful day! 👋"
        
        else:
            return f"🤔 I understood: **{command}**\n\nTry asking me about:\n• Weather in [city]\n• Latest news\n• Current time\n• Today's date\n• Set a reminder\n• Or just say hello!"
    
    def extract_city_from_command(self, command):
        """Extract city name from command"""
        words = command.lower().split()
        for i, word in enumerate(words):
            if word in ['in', 'for', 'at', 'of'] and i + 1 < len(words):
                city_words = [words[i + 1]]
                for j in range(i + 2, len(words)):
                    if words[j] not in ['weather', 'temperature', 'forecast', 'climate']:
                        city_words.append(words[j])
                    else:
                        break
                return ' '.join(city_words).title()
        return None
    
    def get_weather(self):
        """Get weather information"""
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={self.current_city}&appid={self.weather_api_key}&units=metric"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get("cod") != 200:
                return "⚠️ Weather data unavailable for this city."
            
            temp = round(data["main"]["temp"], 1)
            feels_like = round(data["main"]["feels_like"], 1)
            humidity = data["main"]["humidity"]
            description = data["weather"][0]["description"]
            wind_speed = data["wind"]["speed"]
            
            return f"""• **Temperature:** {temp}°C
• **Feels Like:** {feels_like}°C
• **Conditions:** {description.title()}
• **Humidity:** {humidity}%
• **Wind Speed:** {wind_speed} m/s"""
            
        except Exception as e:
            return "⚠️ Weather service is currently unavailable."
    
    def get_news(self):
        """Get news headlines"""
        try:
            url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={self.news_api_key}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get("status") != "ok":
                return "⚠️ News service is currently unavailable."
            
            articles = data["articles"][:5]
            news_items = []
            
            for i, article in enumerate(articles, 1):
                title = article.get("title", "No title").split(' - ')[0]
                source = article.get("source", {}).get("name", "Unknown")
                
                if title and title.lower() != "[removed]":
                    news_items.append(f"{i}. **{title}**\n   📰 Source: {source}")
            
            if not news_items:
                return "No news headlines available at the moment."
            
            return "\n\n".join(news_items)
            
        except Exception as e:
            return "⚠️ News service is currently unavailable."
    
    def set_reminder(self, command):
        """Set a reminder"""
        try:
            reminder_text = command.lower().replace("set reminder", "").replace("remind me", "").replace("to", "").strip()
            
            if reminder_text:
                reminder_text = reminder_text.capitalize()
                reminders = self.load_reminders()
                
                reminders.append({
                    "id": len(reminders) + 1,
                    "text": reminder_text,
                    "time": datetime.datetime.now().strftime("%I:%M %p"),
                    "date": datetime.datetime.now().strftime("%Y-%m-%d")
                })
                
                self.save_reminders(reminders)
                return f"✅ **Reminder set successfully!**\n• **Task:** {reminder_text}\n• **Time:** {datetime.datetime.now().strftime('%I:%M %p')}"
            else:
                return "❌ Please specify what you'd like me to remind you about."
                
        except Exception as e:
            return "❌ Could not set reminder. Please try again."
    
    def show_reminders(self):
        """Show all reminders"""
        try:
            reminders = self.load_reminders()
            
            if not reminders:
                return "📝 You have no reminders set."
            
            reminder_list = []
            for reminder in reminders:
                reminder_list.append(f"• **{reminder['text']}**\n  ⏰ {reminder['time']} | {reminder['date']}")
            
            return f"📋 **Your Reminders:**\n\n" + "\n\n".join(reminder_list)
            
        except Exception as e:
            return "❌ Could not retrieve reminders."
    
    def load_reminders(self):
        """Load reminders from file"""
        try:
            with open("data/reminders.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_reminders(self, reminders):
        """Save reminders to file"""
        with open("data/reminders.json", "w") as f:
            json.dump(reminders, f, indent=2)

# Create global instance
aria = WebARIA()

@app.route('/')
def home():
    """Render main page"""
    return render_template('index.html')

@app.route('/api/command', methods=['POST'])
def handle_command():
    """Handle user commands"""
    try:
        data = request.json
        command = data.get('command', '').strip()
        
        if not command:
            return jsonify({
                "response": "❌ Please provide a command.",
                "city": aria.current_city
            }), 400
        
        # Process the command
        response = aria.process_command(command)
        
        return jsonify({
            "response": response,
            "city": aria.current_city,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "response": "❌ An error occurred. Please try again.",
            "city": aria.current_city
        }), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "online",
        "service": "ARIA Web Assistant",
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.route('/api/weather')
def get_weather_api():
    """Get weather API endpoint"""
    weather_info = aria.get_weather()
    return jsonify({
        "city": aria.current_city,
        "weather": weather_info
    })

@app.route('/api/news')
def get_news_api():
    """Get news API endpoint"""
    news_info = aria.get_news()
    return jsonify({
        "news": news_info
    })

@app.route('/api/reminders', methods=['GET', 'POST'])
def handle_reminders_api():
    """Handle reminders API"""
    if request.method == 'POST':
        data = request.json
        command = data.get('command', '').strip()
        if command:
            response = aria.set_reminder(command)
            return jsonify({"message": response})
    
    # GET request - return all reminders
    reminders = aria.load_reminders()
    return jsonify({"reminders": reminders})

if __name__ == "__main__":
    # Create reminders file if it doesn't exist
    if not os.path.exists('data/reminders.json'):
        with open('data/reminders.json', 'w') as f:
            json.dump([], f)
    
    # Run the app on Render-compatible port
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        debug=False
    )
