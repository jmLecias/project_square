from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Example configuration
workers = 1
worker_class = 'eventlet'
timeout = 3600
bind = '0.0.0.0:5000'
loglevel = 'debug'
