import sqlite3
import requests
from flask import Flask, render_template, request, redirect, url_for, g
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import os
from datetime import datetime

app = Flask(__name__)
app.config['DATABASE'] = 'news_aggregator.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this in a real application
NEWS_API_KEY = 'YOUR_NEWS_API_KEY'  # Replace with your NewsAPI key

# Database Initialization
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row  # Access columns by name
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Create database if it doesn't exist
if not os.path.exists(app.config['DATABASE']):
    init_db()

# News Fetching Functions
def fetch_news(keyword):
    url = f'https://newsapi.org/v2/everything?q={keyword}&apiKey={NEWS_API_KEY}'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        return data.get('articles', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news for {keyword}: {e}")
        return []

def store_article(db, keyword, article):
    try:
        db.execute(
            'INSERT INTO articles (keyword, title, source, description, url, published_at) VALUES (?, ?, ?, ?, ?, ?)',
            (
                keyword,
                article.get('title', 'No Title'),
                article.get('source', {}).get('name', 'Unknown Source'),
                article.get('description', 'No Description'),
                article.get('url', '#'),
                article.get('publishedAt')
            )
        )
        db.commit()
    except sqlite3.IntegrityError:
        # Ignore duplicate articles
        pass
    except Exception as e:
        print(f"Error storing article: {e}")

def fetch_and_store_news():
    with app.app_context():
        db = get_db()
        keywords = [row['keyword'] for row in db.execute('SELECT keyword FROM keywords').fetchall()]
        for keyword in keywords:
            articles = fetch_news(keyword)
            for article in articles:
                store_article(db, keyword, article)
        print("News fetched and stored.")

# Background Task
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(fetch_and_store_news, 'interval', minutes=30)  # Adjust interval as needed
scheduler.start()
atexit.register(lambda: scheduler.shutdown(wait=False))

# Routes
@app.route('/')
def index():
    db = get_db()
    keyword_filter = request.args.get('keyword')
    if keyword_filter:
        articles = db.execute('SELECT * FROM articles WHERE keyword = ? ORDER BY published_at DESC', (keyword_filter,)).fetchall()
    else:
        articles = db.execute('SELECT * FROM articles ORDER BY published_at DESC').fetchall()
    keywords = db.execute('SELECT keyword FROM keywords').fetchall()
    return render_template('index.html', articles=articles, keywords=keywords, selected_keyword=keyword_filter)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    db = get_db()
    if request.method == 'POST':
        keyword = request.form['keyword']
        db.execute('INSERT INTO keywords (keyword) VALUES (?)', (keyword,))
        db.commit()
        return redirect(url_for('settings'))
    keywords = db.execute('SELECT keyword FROM keywords').fetchall()
    return render_template('settings.html', keywords=keywords)

@app.route('/delete_keyword', methods=['POST'])
def delete_keyword():
    db = get_db()
    keyword = request.form['keyword']
    db.execute('DELETE FROM keywords WHERE keyword = ?', (keyword,))
    db.commit()
    return redirect(url_for('settings'))

if __name__ == '__main__':
    app.run(debug=True)
```

```sql
CREATE TABLE IF NOT EXISTS keywords (
    keyword TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT,
    title TEXT NOT NULL,
    source TEXT,
    description TEXT,
    url TEXT NOT NULL UNIQUE,
    published_at TEXT,
    FOREIGN KEY (keyword) REFERENCES keywords (keyword)
);
```

```html
<!DOCTYPE html>
<html>
<head>
    <title>Personalized News Aggregator</title>
    <style>
        body {
            font-family: sans-serif;
        }
        .news-article {
            border: 1px solid #ccc;
            margin-bottom: 10px;
            padding: 10px;
        }
        .news-article h2 {
            margin-top: 0;
        }
    </style>
</head>
<body>
    <h1>Personalized News Aggregator</h1>
    <a href="{{ url_for('settings') }}">Settings</a>

    <h2>News Feed</h2>

    <form method="GET">
        <label for="keyword">Filter by Keyword:</label>
        <select name="keyword" id="keyword">
            <option value="">All Keywords</option>
            {% for keyword in keywords %}
                <option value="{{ keyword.keyword }}" {% if keyword.keyword == selected_keyword %}selected{% endif %}>{{ keyword.keyword }}</option>
            {% endfor %}
        </select>
        <button type="submit">Filter</button>
    </form>
    <br>

    {% for article in articles %}
        <div class="news-article">
            <h2>{{ article.title }}</h2>
            <p>Source: {{ article.source }}</p>
            <p>{{ article.description }}</p>
            <p>Published: {{ article.published_at }}</p>
            <a href="{{ article.url }}" target="_blank">Read More</a>
        </div>
    {% endfor %}

</body>
</html>
```

```html
<!DOCTYPE html>
<html>
<head>
    <title>Settings</title>
</head>
<body>
    <h1>Settings</h1>

    <h2>Add Keyword</h2>
    <form method="POST">
        <label for="keyword">Keyword:</label>
        <input type="text" id="keyword" name="keyword" required>
        <button type="submit">Add</button>
    </form>

    <h2>Current Keywords</h2>
    <ul>
        {% for keyword in keywords %}
            <li>
                {{ keyword.keyword }}
                <form method="POST" action="{{ url_for('delete_keyword') }}" style="display: inline;">
                    <input type="hidden" name="keyword" value="{{ keyword.keyword }}">
                    <button type="submit">Delete</button>
                </form>
            </li>
        {% endfor %}
    </ul>

    <a href="{{ url_for('index') }}">Back to News Feed</a>
</body>
</html>