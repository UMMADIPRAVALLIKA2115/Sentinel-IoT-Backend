import os, requests, datetime, random
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_file
# ... other imports ...

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'any_secret_string_123')

# --- 2. CONFIGURATION (FOR CLOUD) ---
# This looks for the keys you typed in the Render Dashboard
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# --- DEBUGGING LOG (See this in Render Logs) ---
if not TOKEN:
    print("❌ ERROR: TELEGRAM_TOKEN not found in environment!")
if not CHAT_ID:
    print("❌ ERROR: TELEGRAM_CHAT_ID not found in environment!")