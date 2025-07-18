import os
import json
import datetime
import time
import logging
import random
from typing import List, Dict, Optional

# Third-party libraries
import tweepy
import facebook
from instagrapi import Client
from linkedin_v2 import LinkedInHelper, ShareEntities
from jinja2 import Environment, FileSystemLoader
import openai
import schedule
import redis
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# API Keys and Secrets (Move these to environment variables for security)
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")

INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
LINKEDIN_RETURN_URL = os.getenv("LINKEDIN_RETURN_URL")
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")  # Store refresh token too

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Redis Client
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

# Jinja2 Environment Setup
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
env = Environment(loader=FileSystemLoader(template_dir))

# --- Authentication Helpers ---

def authenticate_twitter():
    """Authenticates with Twitter API."""
    try:
        auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
        auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        api.verify_credentials()
        logging.info("Twitter authentication successful.")
        return api
    except tweepy.TweepyException as e:
        logging.error(f"Twitter authentication failed: {e}")
        return None

def authenticate_facebook():
    """Authenticates with Facebook API."""
    try:
        graph = facebook.GraphAPI(access_token=FACEBOOK_ACCESS_TOKEN, version="v17.0")
        graph.get_object("me")
        logging.info("Facebook authentication successful.")
        return graph
    except facebook.GraphAPIError as e:
        logging.error(f"Facebook authentication failed: {e}")
        return None

def authenticate_instagram():
    """Authenticates with Instagram API."""
    try:
        client = Client()
        client.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        logging.info("Instagram authentication successful.")
        return client
    except Exception as e:
        logging.error(f"Instagram authentication failed: {e}")
        return None

def authenticate_linkedin():
  """Authenticates with LinkedIn API."""
  try:
    linkedin_helper = LinkedInHelper(
        client_id=LINKEDIN_CLIENT_ID,
        client_secret=LINKEDIN_CLIENT_SECRET,
        return_url=LINKEDIN_RETURN_URL
    )
    # Assuming you have a stored access token.  Handle token refresh if needed.
    linkedin_helper.client.set_access_token(LINKEDIN_ACCESS_TOKEN)
    logging.info("LinkedIn authentication successful.")
    return linkedin_helper
  except Exception as e:
    logging.error(f"LinkedIn authentication failed: {e}")
    return None


# --- Content Generation Helpers ---

def generate_caption_with_gpt3(prompt: str) -> str:
    """Generates a caption using GPT-3."""
    try:
        openai.api_key = OPENAI_API_KEY
        response = openai.Completion.create(
            engine="text-davinci-003",  # Or another suitable engine
            prompt=prompt,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )
        caption = response.choices[0].text.strip()
        return caption
    except Exception as e:
        logging.error(f"GPT-3 caption generation failed: {e}")
        return ""

def render_template(template_name: str, data: Dict) -> str:
    """Renders a Jinja2 template with the given data."""
    try:
        template = env.get_template(template_name)
        return template.render(data)
    except Exception as e:
        logging.error(f"Template rendering failed: {e}")
        return ""

# --- Posting Functions ---

def post_to_twitter(api: tweepy.API, message: str, image_path: Optional[str] = None):
    """Posts a message to Twitter with optional image."""
    try:
        if image_path:
            api.update_status_with_media(message, image_path)
        else:
            api.update_status(message)
        logging.info(f"Posted to Twitter: {message}")
    except tweepy.TweepyException as e:
        logging.error(f"Failed to post to Twitter: {e}")

def post_to_facebook(graph: facebook.GraphAPI, message: str, image_path: Optional[str] = None):
    """Posts a message to Facebook with optional image."""
    try:
        if image_path:
            with open(image_path, 'rb') as image:
                graph.put_photo(image=image, message=message, album_path=FACEBOOK_PAGE_ID + "/photos")
        else:
             graph.put_object(FACEBOOK_PAGE_ID, "feed", message=message)
        logging.info(f"Posted to Facebook: {message}")
    except facebook.GraphAPIError as e:
        logging.error(f"Failed to post to Facebook: {e}")

def post_to_instagram(client: Client, message: str, image_path: str):
    """Posts a message to Instagram with image."""
    try:
        client.photo_upload(image_path, message)
        logging.info(f"Posted to Instagram: {message}")
    except Exception as e:
        logging.error(f"Failed to post to Instagram: {e}")

def post_to_linkedin(linkedin_helper: LinkedInHelper, message: str, image_path: Optional[str] = None):
    """Posts a message to LinkedIn with optional image."""
    try:
        share = {
            'comment': message,
            'visibility': 'PUBLIC' # Change if needed
        }

        if image_path:
            # Not fully implemented due to complexity of LinkedIn API image uploads.
            # Requires uploading to LinkedIn's asset system first.
            logging.warning("Image posting to LinkedIn not fully implemented.")
            pass # Placeholder -  Implement image upload flow.
        else:
            linkedin_helper.post_share(share)

        logging.info(f"Posted to LinkedIn: {message}")
    except Exception as e:
        logging.error(f"Failed to post to LinkedIn: {e}")


# --- Scheduling and Management ---

def schedule_post(platform: str, message: str, schedule_time: datetime.datetime, image_path: Optional[str] = None):
    """Schedules a post for a specific platform and time."""
    post_data = {
        'platform': platform,
        'message': message,
        'image_path': image_path,
    }
    redis_client.set(f"post:{schedule_time.isoformat()}:{platform}:{random.randint(1000,9999)}", json.dumps(post_data)) #Unique Key


def process_scheduled_posts():
    """Checks for and processes scheduled posts."""
    now = datetime.datetime.now()
    for key in redis_client.scan_iter("post:*"):
        try:
            post_key = key.decode('utf-8')
            parts = post_key.split(":")
            scheduled_time_str = parts[1]
            scheduled_time = datetime.datetime.fromisoformat(scheduled_time_str)

            if scheduled_time <= now:
                post_data_json = redis_client.get(post_key)
                if post_data_json:
                   post_data = json.loads(post_data_json.decode('utf-8'))
                   platform = post_data['platform']
                   message = post_data['message']
                   image_path = post_data.get('image_path') # Optional
                   try:
                       if platform == 'twitter':
                           api = authenticate_twitter()
                           if api:
                               post_to_twitter(api, message, image_path)
                       elif platform == 'facebook':
                           graph = authenticate_facebook()
                           if graph:
                               post_to_facebook(graph, message, image_path)
                       elif platform == 'instagram':
                           client = authenticate_instagram()
                           if client:
                               post_to_instagram(client, message, image_path)
                       elif platform == 'linkedin':
                           linkedin_helper = authenticate_linkedin()
                           if linkedin_helper:
                               post_to_linkedin(linkedin_helper, message, image_path)
                       else:
                           logging.warning(f"Unknown platform: {platform}")
                   except Exception as e:
                       logging.error(f"Error processing scheduled post: {e}")
                   finally:
                       redis_client.delete(post_key) # Remove after processing
        except Exception as e:
            logging.error(f"Error iterating through Redis keys: {e}")



# --- Main Function ---

def main():
    """Main function to run the social media poster."""
    # Example usage:

    # 1. Generate content using a template
    template_data = {'title': 'Exciting News!', 'content': 'Check out our latest blog post!'}
    message = render_template('default_post.txt', template_data)

    # 2. Generate a caption using GPT-3
    caption_prompt = "Write a short, engaging caption for a social media post about a new product launch."
    caption = generate_caption_with_gpt3(caption_prompt)
    if caption:
        message = f"{message}\n\n{caption}" # Combine template with AI caption

    # 3. Schedule a post for Twitter in 5 minutes
    schedule_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
    schedule_post('twitter', message, schedule_time, 'path/to/image.jpg') # Replace with actual image path

    # 4.  Schedule for other platforms similarly.
    schedule_time_fb = datetime.datetime.now() + datetime.timedelta(minutes=7)
    schedule_post('facebook', "Check out my cool webpage!  Visit: www.example.com", schedule_time_fb)

    # 5. Periodically check and process scheduled posts (e.g., every minute)
    schedule.every(1).minute.do(process_scheduled_posts)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()