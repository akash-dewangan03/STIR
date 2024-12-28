import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
from run_selenium import main as run_data_extraction
from pymongo import MongoClient
import logging

# Load environment variables
load_dotenv(".env")

# Initialize Flask application
app = Flask(__name__)

# Logging configuration
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# MongoDB connection
mongo_client = MongoClient(os.getenv('mongodb_uri'))
database = mongo_client.twitter_data
trends_collection = database.trending_topics

@app.route('/')
def home_page():
    # Retrieve the latest trending data from MongoDB
    trends = list(trends_collection.find(sort=[('timestamp', -1)], projection={'_id': False}))
    recent_trend = trends[0] if trends else {}
    return render_template('index.html', trend=recent_trend)

@app.route('/scrape', methods=['POST'])
def initiate_scrape():
    log.info("Initiating data scraping...")
    try:
        run_data_extraction()
        log.info("Data scraping completed successfully.")
    except Exception as err:
        log.error(f"Error during scraping: {err}")
    return redirect(url_for('home_page'))

if __name__ == '__main__':
    app.run(debug=True)