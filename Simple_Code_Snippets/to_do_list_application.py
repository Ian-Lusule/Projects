import os
import json
import datetime
import uuid
import threading
import time
import logging

# Install necessary libraries:
# pip install firebase_admin flask flask_cors SpeechRecognition pydub
# You may need to install portaudio for SpeechRecognition: brew install portaudio
# Or on other systems: sudo apt-get install libportaudio2 libportaudi0 libportaudio-dev

# Placeholder imports - replace with actual implementation details
import firebase_admin
from firebase_admin import credentials, firestore, auth
from flask import Flask, request, jsonify
from flask_cors import CORS
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence

# Configuration
DATABASE_URL = os.environ.get('DATABASE_URL') or 'YOUR_FIREBASE_DATABASE_URL'  # Firebase database URL
CREDENTIALS_PATH = os.environ.get('CREDENTIALS_PATH') or 'path/to/your/firebase_credentials.json'  # Path to Firebase credentials
ALLOWED_ORIGINS = ["http://localhost:3000", "https://your-domain.com"]  # Replace with your actual origins

# Firebase setup
cred = credentials.Certificate(CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Flask app setup
app = Flask(__name__)
CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=True)

# Helper Functions

def create_uuid():
    return str(uuid.uuid4())

def serialize_document(doc):
    """Convert Firestore document to a JSON-serializable dictionary."""
    data = doc.to_dict()
    if data:
        data['id'] = doc.id
        return data
    return None

def deserialize_document(data):
    """Convert a dictionary to Firestore-compatible data.  Removes 'id'."""
    if 'id' in data:
        del data['id']
    return data

# Authentication Decorator
def authenticate(func):
    """Authentication decorator to verify user tokens."""
    def wrapper(*args, **kwargs):
        try:
            id_token = request.headers.get('Authorization').split(' ')[1]  # Assuming Bearer token
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            kwargs['user_id'] = uid  # Pass user_id to the decorated function
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Authentication error: {e}")
            return jsonify({'error': 'Unauthorized'}), 401
    wrapper.__name__ = func.__name__  # Preserve original function name
    return wrapper

# Data Models (Simplified for the example)
class Task:
    def __init__(self, title, description, due_date=None, priority='low', project=None, category=None, completed=False, shared_with=None, created_by=None):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.priority = priority
        self.project = project
        self.category = category
        self.completed = completed
        self.shared_with = shared_with or []
        self.created_by = created_by # User ID of creator

    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'priority': self.priority,
            'project': self.project,
            'category': self.category,
            'completed': self.completed,
            'shared_with': self.shared_with,
            'created_by': self.created_by
        }

    @classmethod
    def from_dict(cls, data):
         due_date = datetime.datetime.fromisoformat(data['due_date']) if data.get('due_date') else None
         return cls(
                title=data['title'],
                description=data['description'],
                due_date=due_date,
                priority=data['priority'],
                project=data['project'],
                category=data['category'],
                completed=data['completed'],
                shared_with=data['shared_with'],
                created_by=data['created_by']
            )


# API Endpoints

@app.route('/api/register', methods=['POST'])
def register():
    """Registers a new user."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    try:
        user = auth.create_user(
            email=email,
            password=password
        )
        return jsonify({'message': 'User created successfully', 'uid': user.uid}), 201
    except Exception as e:
        logging.error(f"Registration error: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/login', methods=['POST'])
def login():
    """Placeholder for user login.  Authentication happens on the client side."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')  # In reality, handle this securely on the client.

    # Authentication with Firebase is typically done client-side.
    # This endpoint would primarily be used to verify credentials if you were
    # implementing a custom authentication system, which is not recommended with Firebase.

    return jsonify({'message': 'Login successful (client-side authentication required)'}), 200


@app.route('/api/tasks', methods=['POST'])
@authenticate
def create_task(user_id):
    """Creates a new task."""
    try:
        data = request.get_json()
        task = Task(
            title=data.get('title'),
            description=data.get('description'),
            due_date=datetime.datetime.fromisoformat(data.get('due_date')) if data.get('due_date') else None,
            priority=data.get('priority'),
            project=data.get('project'),
            category=data.get('category'),
            created_by=user_id
        )

        task_dict = task.to_dict()
        tasks_collection = db.collection('tasks')
        _, doc_ref = tasks_collection.add(task_dict)

        # After creating, immediately fetch and return the created task, including the document ID
        new_task = serialize_document(doc_ref.get())
        return jsonify(new_task), 201

    except Exception as e:
        logging.error(f"Error creating task: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/tasks', methods=['GET'])
@authenticate
def list_tasks(user_id):
    """Lists all tasks for a specific user."""
    try:
        tasks_ref = db.collection('tasks')
        query = tasks_ref.where('created_by', '==', user_id)
        docs = query.stream()

        tasks = [serialize_document(doc) for doc in docs]

        # Remove None values resulting from documents that failed to serialize
        tasks = [task for task in tasks if task]

        return jsonify(tasks), 200
    except Exception as e:
        logging.error(f"Error listing tasks: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/tasks/<task_id>', methods=['GET'])
@authenticate
def get_task(task_id, user_id):
    """Gets a specific task by ID."""
    try:
        task_ref = db.collection('tasks').document(task_id)
        doc = task_ref.get()

        if not doc.exists:
            return jsonify({'error': 'Task not found'}), 404

        task = serialize_document(doc)

        if task['created_by'] != user_id:  # Simple authorization check
            return jsonify({'error': 'Unauthorized'}), 403

        return jsonify(task), 200
    except Exception as e:
        logging.error(f"Error getting task: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<task_id>', methods=['PUT'])
@authenticate
def update_task(task_id, user_id):
    """Updates a specific task by ID."""
    try:
        data = request.get_json()
        task_ref = db.collection('tasks').document(task_id)
        doc = task_ref.get()

        if not doc.exists:
            return jsonify({'error': 'Task not found'}), 404

        task = serialize_document(doc)

        if task['created_by'] != user_id:  # Simple authorization check
            return jsonify({'error': 'Unauthorized'}), 403


        # Update only provided fields.  Do NOT blindly overwrite, or created_by can be removed.
        updates = {}
        if 'title' in data:
            updates['title'] = data['title']
        if 'description' in data:
            updates['description'] = data['description']
        if 'due_date' in data:
            updates['due_date'] = datetime.datetime.fromisoformat(data['due_date']) if data['due_date'] else None #Handle possible empty date strings
        if 'priority' in data:
            updates['priority'] = data['priority']
        if 'project' in data:
            updates['project'] = data['project']
        if 'category' in data:
            updates['category'] = data['category']
        if 'completed' in data:
            updates['completed'] = data['completed']
        if 'shared_with' in data:
            updates['shared_with'] = data['shared_with']

        if updates:
             task_ref.update(updates)

        updated_task = serialize_document(task_ref.get()) # Fetch the updated document
        return jsonify(updated_task), 200
    except Exception as e:
        logging.error(f"Error updating task: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/tasks/<task_id>', methods=['DELETE'])
@authenticate
def delete_task(task_id, user_id):
    """Deletes a specific task by ID."""
    try:
        task_ref = db.collection('tasks').document(task_id)
        doc = task_ref.get()

        if not doc.exists:
            return jsonify({'error': 'Task not found'}), 404

        task = serialize_document(doc)

        if task['created_by'] != user_id:  # Simple authorization check
            return jsonify({'error': 'Unauthorized'}), 403

        task_ref.delete()
        return jsonify({'message': 'Task deleted successfully'}), 200
    except Exception as e:
        logging.error(f"Error deleting task: {e}")
        return jsonify({'error': str(e)}), 500



@app.route('/api/share_task/<task_id>', methods=['POST'])
@authenticate
def share_task(task_id, user_id):
    """Shares a task with another user."""
    try:
        data = request.get_json()
        share_with_email = data.get('email')

        try:
            shared_user = auth.get_user_by_email(share_with_email)
            shared_user_id = shared_user.uid
        except auth.UserNotFoundError:
            return jsonify({'error': 'User not found'}), 404

        task_ref = db.collection('tasks').document(task_id)
        doc = task_ref.get()

        if not doc.exists:
            return jsonify({'error': 'Task not found'}), 404

        task = serialize_document(doc)

        if task['created_by'] != user_id:  # Simple authorization check
            return jsonify({'error': 'Unauthorized'}), 403

        # Atomically add the user to the 'shared_with' array.  No duplicates allowed.
        task_ref.update({
            'shared_with': firestore.ArrayUnion([shared_user_id])
        })

        return jsonify({'message': f'Task shared with {share_with_email} successfully'}), 200
    except Exception as e:
        logging.error(f"Error sharing task: {e}")
        return jsonify({'error': str(e)}), 500

# Voice Input (Basic Example)
@app.route('/api/voice_to_text', methods=['POST'])
@authenticate
def voice_to_text(user_id):
    """Converts voice input to text."""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']
        filename = audio_file.filename

        # Save the audio file temporarily
        temp_audio_path = os.path.join('/tmp', filename) # Ensure /tmp exists or use a different directory
        audio_file.save(temp_audio_path)

        # Convert to WAV if necessary (speech_recognition prefers WAV)
        if not filename.lower().endswith('.wav'):
            try:
                sound = AudioSegment.from_file(temp_audio_path)
                wav_path = os.path.join('/tmp', 'temp_audio.wav') # Ensure /tmp exists
                sound.export(wav_path, format="wav")
                temp_audio_path = wav_path  # Use the WAV file
            except Exception as e:
                logging.error(f"Audio conversion error: {e}")
                return jsonify({'error': 'Audio conversion failed'}), 500

        r = sr.Recognizer()
        with sr.AudioFile(temp_audio_path) as source:
            audio = r.record(source)

        try:
            text = r.recognize_google(audio)
            return jsonify({'text': text}), 200
        except sr.UnknownValueError:
            return jsonify({'text': 'Could not understand audio'}), 200
        except sr.RequestError as e:
            logging.error(f"Could not request results from Google Speech Recognition service; {e}")
            return jsonify({'error': 'Could not request results from Google Speech Recognition service'}), 500

        finally:
            # Clean up the temporary file
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
    except Exception as e:
        logging.error(f"Voice recognition error: {e}")
        return jsonify({'error': str(e)}), 500

# Background Task (Push Notifications - Placeholder)
def send_push_notification(user_id, message):
    """Placeholder function for sending push notifications."""
    # In a real application, you would use a service like Firebase Cloud Messaging (FCM)
    # or AWS Pinpoint to send push notifications to the user's device.
    logging.info(f"Simulating push notification to user {user_id}: {message}")

def monitor_tasks():
    """Background task to monitor tasks and send reminders."""
    while True:
        try:
            now = datetime.datetime.now()
            tasks_ref = db.collection('tasks')
            docs = tasks_ref.where('due_date', '<=', now + datetime.timedelta(minutes=30)).where('completed', '==', False).stream()  # Check tasks due within 30 minutes

            for doc in docs:
                task = serialize_document(doc)
                if task: # Avoid processing failed deserializations
                    user_id = task['created_by']
                    message = f"Reminder: Task '{task['title']}' is due soon!"
                    send_push_notification(user_id, message)
                    # Optionally, mark the task as 'reminder_sent' to avoid repeated notifications

        except Exception as e:
            logging.error(f"Error in background task: {e}")

        time.sleep(60)  # Check every minute

# Start the background task
notification_thread = threading.Thread(target=monitor_tasks)
notification_thread.daemon = True  # Allow the app to exit even if the thread is running
notification_thread.start()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))