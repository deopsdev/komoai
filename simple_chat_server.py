#!/usr/bin/env python3
"""
Simple Python server for Komo AI chat functionality.
This replaces the Node.js server.js when node is not available.
"""

import http.server
import socketserver
import json
import random
from datetime import datetime

PORT = 3040

class ChatHandler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_cors_headers()
        self.send_response(204)
        self.end_headers()
    
    def send_cors_headers(self):
        """Set CORS headers for cross-origin requests"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/chat':
            self.handle_chat()
        else:
            self.send_error(404, "Not Found")
    
    def handle_chat(self):
        """Handle chat requests to AI"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if not data or 'messages' not in data:
                self.send_error(400, "Invalid request data")
                return
            
            messages = data['messages']
            
            # Get the last user message
            last_user_message = ""
            for msg in reversed(messages):
                if msg.get('role') == 'user':
                    last_user_message = msg.get('content', '')
                    break
            
            # Improved AI responses based on keywords (ELIZA-like)
            lower_msg = last_user_message.lower()
            
            if not last_user_message:
                reply = "Hello! I'm Komo AI. How can I help you today?"
            elif 'hello' in lower_msg or 'hi' in lower_msg:
                reply = "Hello! I'm Komo AI, your privacy-first assistant. How can I help you today?"
            elif 'help' in lower_msg:
                reply = "I'm here to help! I can assist you with various topics while keeping your privacy secure. What would you like to know?"
            elif 'privacy' in lower_msg:
                reply = "Privacy is my top priority! I automatically redact personal information like emails, phone numbers, and other sensitive data."
            elif 'thank' in lower_msg:
                reply = "You're welcome! Feel free to ask me anything else."
            elif 'bye' in lower_msg or 'goodbye' in lower_msg:
                reply = "Goodbye! Have a great day. I'm always here when you need help."
            elif 'time' in lower_msg:
                reply = f"The current server time is {datetime.now().strftime('%H:%M:%S')}."
            elif 'date' in lower_msg:
                reply = f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."
            elif 'who are you' in lower_msg or 'your name' in lower_msg:
                reply = "I am Komo AI, a simple but helpful virtual assistant running locally on your machine."
            elif '?' in lower_msg:
                # Generic question handling
                responses = [
                    "That's an interesting question. I'm still learning, but I'll do my best to help.",
                    "I'm not sure about that yet, but I can help with other things!",
                    "Could you elaborate on that?",
                    "I think the answer depends on context. Can you provide more details?"
                ]
                reply = random.choice(responses)
            else:
                # Contextual echo
                responses = [
                    f"I understand. You said '{last_user_message}'. Tell me more.",
                    "Interesting. Please go on.",
                    "I see. How does that make you feel?",
                    "Okay, I'm listening."
                ]
                reply = random.choice(responses)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            
            response_data = {
                "reply": reply,
                "model": "Komo-AI-Simple",
                "timestamp": datetime.now().isoformat()
            }
            
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            
        except Exception as e:
            # Send 500 with CORS headers
            self.send_response(500)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Internal server error: {str(e)}"}).encode('utf-8'))
    
    def do_GET(self):
        """Handle GET requests - serve static files"""
        if self.path == '/':
            self.path = '/index.html'
        elif self.path == '/chat':
            # Handle GET to chat endpoint
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "Chat endpoint ready"}).encode('utf-8'))
            return
        
        # Serve static files
        return super().do_GET()

def run_server():
    """Run the server"""
    with socketserver.TCPServer(("", PORT), ChatHandler) as httpd:
        print(f"Komo AI Server running at http://localhost:{PORT}")
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    run_server()