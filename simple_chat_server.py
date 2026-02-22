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
            
            # Simple AI responses based on keywords
            if not last_user_message:
                reply = "Hello! I'm Komo AI. How can I help you today?"
            elif 'hello' in last_user_message.lower() or 'hi' in last_user_message.lower():
                reply = "Hello! I'm Komo AI, your privacy-first assistant. How can I help you today?"
            elif 'help' in last_user_message.lower():
                reply = "I'm here to help! I can assist you with various topics while keeping your privacy secure. What would you like to know?"
            elif 'privacy' in last_user_message.lower():
                reply = "Privacy is my top priority! I automatically redact personal information like emails, phone numbers, and other sensitive data."
            elif 'thank' in last_user_message.lower():
                reply = "You're welcome! Feel free to ask me anything else."
            elif 'bye' in last_user_message.lower() or 'goodbye' in last_user_message.lower():
                reply = "Goodbye! Have a great day. I'm always here when you need help."
            else:
                # Generic responses
                responses = [
                    "I'm here to help! What would you like to know?",
                    "That's an interesting question. Let me think about it...",
                    "I understand you're asking about something. Could you provide more details?",
                    "I'm Komo AI, your helpful assistant. How can I assist you with this?",
                    "Thanks for your question! I'm here to provide helpful and accurate information."
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
            self.send_error(500, f"Internal server error: {str(e)}")
    
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