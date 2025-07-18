import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import datetime
import time
import schedule
import threading
import logging
import json
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64

try:
    import tweepy
    import facebook
except ImportError:
    print("Please install required packages: tweepy, facebook, schedule, cryptography, pillow")
    exit()

from PIL import Image, ImageTk

# Configuration File
CONFIG_FILE = "config.json"
LOG_FILE = "poster.log"
ENCRYPTION_KEY_FILE = "encryption.key"

# Logging setup
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class CredentialsManager:
    def __init__(self, encryption_key_file=ENCRYPTION_KEY_FILE):
        self.encryption_key_file = encryption_key_file
        self.encryption_key = self._load_or_generate_key()

    def _load_or_generate_key(self):
        if os.path.exists(self.encryption_key_file):
            with open(self.encryption_key_file, "rb") as key_file:
                key = key_file.read()
            return key
        else:
            key = Fernet.generate_key()
            with open(self.encryption_key_file, "wb") as key_file:
                key_file.write(key)
            return key
    
    def encrypt(self, data: str) -> str:
        f = Fernet(self.encryption_key)
        encrypted_data = f.encrypt(data.encode())
        return encrypted_data.decode()
    
    def decrypt(self, data: str) -> str:
        f = Fernet(self.encryption_key)
        decrypted_data = f.decrypt(data.encode()).decode()
        return decrypted_data

class SocialMediaPoster:
    def __init__(self, master):
        self.master = master
        master.title("Automated Social Media Poster")

        self.credentials_manager = CredentialsManager()

        self.twitter_api = None
        self.facebook_api = None
        self.scheduled_posts = []

        # Load configuration
        self.config = self.load_config()

        # UI elements
        self.create_widgets()

        # Background scheduler
        self.stop_scheduler = threading.Event()
        self.scheduler_thread = threading.Thread(target=self.run_scheduler)
        self.scheduler_thread.daemon = True  # Allow main thread to exit even if this is running
        self.scheduler_thread.start()

    def create_widgets(self):
        # Notebook (Tabs)
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Credentials Tab
        self.credentials_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.credentials_tab, text="Credentials")
        self.create_credentials_tab()

        # Schedule Tab
        self.schedule_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.schedule_tab, text="Schedule Post")
        self.create_schedule_tab()

        # Queue Tab
        self.queue_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.queue_tab, text="Scheduled Queue")
        self.create_queue_tab()

    def create_credentials_tab(self):
        ttk.Label(self.credentials_tab, text="Twitter API Key:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.twitter_api_key_entry = ttk.Entry(self.credentials_tab, width=50)
        self.twitter_api_key_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(self.credentials_tab, text="Twitter API Secret:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.twitter_api_secret_entry = ttk.Entry(self.credentials_tab, width=50, show="*")
        self.twitter_api_secret_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(self.credentials_tab, text="Twitter Access Token:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.twitter_access_token_entry = ttk.Entry(self.credentials_tab, width=50, show="*")
        self.twitter_access_token_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(self.credentials_tab, text="Twitter Access Secret:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.twitter_access_secret_entry = ttk.Entry(self.credentials_tab, width=50, show="*")
        self.twitter_access_secret_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(self.credentials_tab, text="Facebook Page ID:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.facebook_page_id_entry = ttk.Entry(self.credentials_tab, width=50)
        self.facebook_page_id_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(self.credentials_tab, text="Facebook Access Token:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.facebook_access_token_entry = ttk.Entry(self.credentials_tab, width=50, show="*")
        self.facebook_access_token_entry.grid(row=5, column=1, sticky="ew", padx=5, pady=5)

        # Load Credentials from config
        if self.config and self.config.get("credentials"):
            credentials = self.config["credentials"]
            self.twitter_api_key_entry.insert(0, credentials.get("twitter_api_key", ""))
            self.twitter_api_secret_entry.insert(0, credentials.get("twitter_api_secret", ""))
            self.twitter_access_token_entry.insert(0, credentials.get("twitter_access_token", ""))
            self.twitter_access_secret_entry.insert(0, credentials.get("twitter_access_secret", ""))
            self.facebook_page_id_entry.insert(0, credentials.get("facebook_page_id", ""))
            self.facebook_access_token_entry.insert(0, credentials.get("facebook_access_token", ""))

        save_credentials_button = ttk.Button(self.credentials_tab, text="Save Credentials", command=self.save_credentials)
        save_credentials_button.grid(row=6, column=1, sticky="e", padx=5, pady=10)

    def create_schedule_tab(self):
        ttk.Label(self.schedule_tab, text="Post Content:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.post_content_text = tk.Text(self.schedule_tab, width=60, height=10)
        self.post_content_text.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(self.schedule_tab, text="Image:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.image_path = tk.StringVar()
        self.image_path_entry = ttk.Entry(self.schedule_tab, textvariable=self.image_path, width=50, state="disabled")
        self.image_path_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        browse_button = ttk.Button(self.schedule_tab, text="Browse", command=self.browse_image)
        browse_button.grid(row=1, column=2, sticky="w", padx=5, pady=5)

        ttk.Label(self.schedule_tab, text="Schedule Date/Time:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.schedule_datetime_entry = ttk.Entry(self.schedule_tab, width=30)
        self.schedule_datetime_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        self.schedule_datetime_entry.insert(0, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) # Default Value

        ttk.Label(self.schedule_tab, text="Platforms:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.post_to_twitter = tk.BooleanVar(value=True)
        self.twitter_checkbox = ttk.Checkbutton(self.schedule_tab, text="Twitter", variable=self.post_to_twitter)
        self.twitter_checkbox.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        self.post_to_facebook = tk.BooleanVar(value=True)
        self.facebook_checkbox = ttk.Checkbutton(self.schedule_tab, text="Facebook", variable=self.post_to_facebook)
        self.facebook_checkbox.grid(row=3, column=2, sticky="w", padx=5, pady=5)

        schedule_button = ttk.Button(self.schedule_tab, text="Schedule Post", command=self.schedule_post)
        schedule_button.grid(row=4, column=1, sticky="e", padx=5, pady=10)

    def create_queue_tab(self):
        self.tree = ttk.Treeview(self.queue_tab, columns=('Content', 'Platform', 'Scheduled Time'), show='headings')
        self.tree.heading('Content', text='Content')
        self.tree.heading('Platform', text='Platform')
        self.tree.heading('Scheduled Time', text='Scheduled Time')
        self.tree.column('Content', width=300)
        self.tree.column('Platform', width=100)
        self.tree.column('Scheduled Time', width=150)
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        # Add delete button
        delete_button = ttk.Button(self.queue_tab, text="Delete Post", command=self.delete_selected_post)
        delete_button.pack(pady=5)
        
        self.refresh_queue()

    def browse_image(self):
        filename = filedialog.askopenfilename(initialdir=".", title="Select an Image",
                                              filetypes=(("Image files", "*.jpg;*.jpeg;*.png"), ("all files", "*.*")))
        if filename:
            self.image_path.set(filename)

    def schedule_post(self):
        content = self.post_content_text.get("1.0", tk.END).strip()
        image = self.image_path.get()
        schedule_time_str = self.schedule_datetime_entry.get()
        post_to_twitter = self.post_to_twitter.get()
        post_to_facebook = self.post_to_facebook.get()

        try:
            schedule_time = datetime.datetime.strptime(schedule_time_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            messagebox.showerror("Error", "Invalid date/time format. Use YYYY-MM-DD HH:MM:SS")
            return

        if not content:
            messagebox.showerror("Error", "Post content cannot be empty.")
            return
        
        platforms = []
        if post_to_twitter:
            platforms.append("Twitter")
        if post_to_facebook:
            platforms.append("Facebook")

        if not platforms:
            messagebox.showerror("Error", "Please select at least one platform.")
            return

        self.scheduled_posts.append({
            'content': content,
            'image': image,
            'schedule_time': schedule_time,
            'platforms': platforms
        })

        self.schedule_job(content, image, schedule_time, platforms)
        self.refresh_queue()
        messagebox.showinfo("Success", "Post scheduled successfully.")

    def schedule_job(self, content, image, schedule_time, platforms):
        def post_job():
            try:
                if "Twitter" in platforms:
                    self.post_to_twitter_api(content, image)
                if "Facebook" in platforms:
                    self.post_to_facebook_api(content, image)
                logging.info(f"Successfully posted to {', '.join(platforms)}: {content}")
                messagebox.showinfo("Success", f"Successfully posted to {', '.join(platforms)}: {content}")
            except Exception as e:
                logging.error(f"Error posting to {', '.join(platforms)}: {e}")
                messagebox.showerror("Error", f"Error posting to {', '.join(platforms)}: {e}")
            finally:
                # Remove the post from the scheduled_posts list after posting
                self.scheduled_posts = [post for post in self.scheduled_posts if post['content'] != content or post['schedule_time'] != schedule_time]
                self.refresh_queue()
                
        schedule_time_str = schedule_time.strftime("%Y-%m-%d %H:%M:%S") # Convert datetime back to string for schedule

        schedule_function = lambda: post_job()

        schedule.every().day.at(schedule_time.strftime("%H:%M:%S")).do(schedule_function)

    def post_to_twitter_api(self, content, image_path=None):
        try:
            if not self.twitter_api:
                self.authenticate_twitter()
            
            if image_path:
                self.twitter_api.update_with_media(image_path, status=content)
            else:
                self.twitter_api.update_status(content)

        except tweepy.TweepyException as e:
            logging.error(f"Twitter API Error: {e}")
            raise e
        except Exception as e:
            logging.error(f"General Error posting to Twitter: {e}")
            raise e

    def post_to_facebook_api(self, content, image_path=None):
        try:
            if not self.facebook_api:
                self.authenticate_facebook()

            if image_path:
                with open(image_path, 'rb') as image_file:
                    self.facebook_api.put_photo(image=image_file, message=content)
            else:
                self.facebook_api.put_object(parent_object='me', connection_name='feed', message=content)

        except facebook.GraphAPIError as e:
            logging.error(f"Facebook API Error: {e}")
            raise e
        except Exception as e:
            logging.error(f"General Error posting to Facebook: {e}")
            raise e
    
    def authenticate_twitter(self):
        try:
            api_key = self.credentials_manager.decrypt(self.config['credentials']['twitter_api_key'])
            api_secret = self.credentials_manager.decrypt(self.config['credentials']['twitter_api_secret'])
            access_token = self.credentials_manager.decrypt(self.config['credentials']['twitter_access_token'])
            access_secret = self.credentials_manager.decrypt(self.config['credentials']['twitter_access_secret'])

            auth = tweepy.OAuthHandler(api_key, api_secret)
            auth.set_access_token(access_token, access_secret)
            self.twitter_api = tweepy.API(auth)
            self.twitter_api.verify_credentials()
            logging.info("Successfully authenticated with Twitter API.")
        except Exception as e:
            logging.error(f"Error authenticating with Twitter: {e}")
            messagebox.showerror("Error", f"Error authenticating with Twitter: {e}")
            raise e

    def authenticate_facebook(self):
        try:
            page_id = self.credentials_manager.decrypt(self.config['credentials']['facebook_page_id'])
            access_token = self.credentials_manager.decrypt(self.config['credentials']['facebook_access_token'])
            self.facebook_api = facebook.GraphAPI(access_token=access_token)
            # Verify authentication (e.g., by fetching page info)
            self.facebook_api.get_object(page_id)  # Replace with actual page ID
            logging.info("Successfully authenticated with Facebook API.")
        except Exception as e:
            logging.error(f"Error authenticating with Facebook: {e}")
            messagebox.showerror("Error", f"Error authenticating with Facebook: {e}")
            raise e
    
    def save_credentials(self):
        twitter_api_key = self.twitter_api_key_entry.get()
        twitter_api_secret = self.twitter_api_secret_entry.get()
        twitter_access_token = self.twitter_access_token_entry.get()
        twitter_access_secret = self.twitter_access_secret_entry.get()
        facebook_page_id = self.facebook_page_id_entry.get()
        facebook_access_token = self.facebook_access_token_entry.get()

        # Encrypt the credentials
        encrypted_twitter_api_key = self.credentials_manager.encrypt(twitter_api_key)
        encrypted_twitter_api_secret = self.credentials_manager.encrypt(twitter_api_secret)
        encrypted_twitter_access_token = self.credentials_manager.encrypt(twitter_access_token)
        encrypted_twitter_access_secret = self.credentials_manager.encrypt(twitter_access_secret)
        encrypted_facebook_page_id = self.credentials_manager.encrypt(facebook_page_id)
        encrypted_facebook_access_token = self.credentials_manager.encrypt(facebook_access_token)
        
        config_data = {
            "credentials": {
                "twitter_api_key": encrypted_twitter_api_key,
                "twitter_api_secret": encrypted_twitter_api_secret,
                "twitter_access_token": encrypted_twitter_access_token,
                "twitter_access_secret": encrypted_twitter_access_secret,
                "facebook_page_id": encrypted_facebook_page_id,
                "facebook_access_token": encrypted_facebook_access_token,
            }
        }

        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(config_data, f, indent=4)
            self.config = config_data
            messagebox.showinfo("Success", "Credentials saved successfully.")
            logging.info("Credentials saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving credentials: {e}")
            logging.error(f"Error saving credentials: {e}")

    def load_config(self):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            logging.warning("Config file is empty or corrupted. Creating a new one.")
            return {}

    def run_scheduler(self):
        while not self.stop_scheduler.is_set():
            schedule.run_pending()
            time.sleep(1)

    def refresh_queue(self):
        # Clear the existing items in the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Repopulate the treeview with the scheduled posts
        for post in self.scheduled_posts:
            self.tree.insert('', 'end', values=(post['content'], ', '.join(post['platforms']), post['schedule_time'].strftime("%Y-%m-%d %H:%M:%S")))

    def delete_selected_post(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select a post to delete.")
            return

        # Get the values of the selected item
        item_values = self.tree.item(selected_item[0], 'values')
        content = item_values[0]
        schedule_time_str = item_values[2]  # The scheduled time as a string
        
        try:
            schedule_time = datetime.datetime.strptime(schedule_time_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            messagebox.showerror("Error", "Invalid date/time format in the queue.")
            return

        # Cancel the scheduled job
        jobs_to_cancel = []
        for job in schedule.jobs:
            if job.tags and content in job.tags: #Assumes content is a tag
                jobs_to_cancel.append(job)

        for job in jobs_to_cancel:
            schedule.cancel_job(job)

        # Remove the post from the scheduled_posts list
        self.scheduled_posts = [post for post in self.scheduled_posts if post['content'] != content or post['schedule_time'] != schedule_time]

        # Refresh the queue
        self.refresh_queue()
        messagebox.showinfo("Success", "Post deleted successfully.")

    def on_closing(self):
        self.stop_scheduler.set()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    poster = SocialMediaPoster(root)
    root.protocol("WM_DELETE_WINDOW", poster.on_closing)  # Handle window close event
    root.mainloop()