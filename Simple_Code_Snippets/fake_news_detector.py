import nltk
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import newspaper
import re
import whois
from datetime import datetime
import dateutil.parser as parser

# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')


from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize

# --- 1. Data Acquisition and Preprocessing ---

def scrape_article(url):
    """Scrapes article text from a given URL using Newspaper3k."""
    try:
        article = newspaper.Article(url)
        article.download()
        article.parse()
        return article.text
    except:
        return None

def clean_text(text):
    """Cleans text by removing punctuation, converting to lowercase, and removing stop words."""
    if text is None:
        return ""
    text = re.sub(r'[^\w\s]', '', text)
    text = text.lower()
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text)
    tokens = [w for w in tokens if not w in stop_words]
    return " ".join(tokens)

# --- 2. Feature Extraction ---

def extract_writing_style_features(text):
    """Extracts features related to writing style: sentence length, word complexity, sentiment."""
    if not text:
        return 0, 0, 0

    sentences = nltk.sent_tokenize(text)
    words = word_tokenize(text)

    avg_sentence_length = len(words) / len(sentences) if sentences else 0
    complex_word_count = sum(1 for word in words if len(word) > 6)
    complex_word_ratio = complex_word_count / len(words) if words else 0

    sid = SentimentIntensityAnalyzer()
    sentiment_scores = sid.polarity_scores(text)
    compound_sentiment = sentiment_scores['compound']

    return avg_sentence_length, complex_word_ratio, compound_sentiment


def extract_source_credibility_features(url):
    """Extracts features related to source credibility: domain age, HTTPS status, Alexa rank."""
    try:
        domain = re.search(r'^(?:https?:\/\/)?(?:[^@\n]+@)?(?:www\.)?', url).group(0)
        domain = domain.replace("www.", "").replace("https://", "").replace("http://", "")
        domain = domain.rstrip('/')

        try:
            w = whois.whois(domain)
            creation_date = w.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]

            domain_age = (datetime.now() - creation_date).days if creation_date else 0
        except Exception as e:
            domain_age = 0

        https_status = url.startswith('https')


        try:
            alexa_rank = get_alexa_rank(domain)
        except:
            alexa_rank = 10000000 # Assign a high rank if retrieval fails


        return domain_age, https_status, alexa_rank
    except:
        return 0, False, 10000000


def get_alexa_rank(domain):
    """Retrieves Alexa rank of a website."""
    url = f"https://www.alexa.com/siteinfo/{domain}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.content, 'html.parser')
        rank_element = soup.find("div", class_="rank-global")

        if rank_element:
            rank_text = rank_element.get_text(strip=True)
            rank = int(rank_text.replace("#", "").replace(",", ""))

            return rank
        else:
             return 10000000 #Assign very large value if alexa rank is unavailable

    except requests.exceptions.RequestException as e:
         return 10000000 #Assign very large value if requests fail.

    except Exception as e:
        return 10000000  #assign very large value if other errors occur


def extract_factual_accuracy_features(text, url):
    """
    Extracts features related to factual accuracy.  This implementation is simplified and requires API keys for full functionality.
    It returns placeholder values.  A complete implementation would involve:
    - Fact-checking APIs (e.g., Google Fact Check Tools API)
    - Knowledge graph lookups (e.g., Wikidata, DBpedia)
    """

    # Placeholder:  A real implementation would query external APIs.
    number_of_citations = 0
    presence_of_errors = 0

    return number_of_citations, presence_of_errors



# --- 3. Model Training ---

def train_model(X, y):
    """Trains a Logistic Regression model."""
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LogisticRegression(max_iter=1000) # Increased max_iter for convergence
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Classification Report:\n", classification_report(y_test, y_pred))
    return model

def create_tfidf_matrix(texts):
    """Creates TF-IDF matrix from a list of texts."""
    vectorizer = TfidfVectorizer(max_features=5000)  # Limit features for performance
    X = vectorizer.fit_transform(texts)
    return X, vectorizer

# --- 4. Prediction ---

def predict_fake_news(url, model, vectorizer):
    """Predicts whether an article at a given URL is fake news."""
    text = scrape_article(url)
    if not text:
        return "Could not retrieve article."

    cleaned_text = clean_text(text)

    # Writing Style Features
    avg_sentence_length, complex_word_ratio, compound_sentiment = extract_writing_style_features(cleaned_text)

    # Source Credibility Features
    domain_age, https_status, alexa_rank = extract_source_credibility_features(url)

    # Factual Accuracy Features (Placeholder)
    number_of_citations, presence_of_errors = extract_factual_accuracy_features(cleaned_text, url)

    # TF-IDF Features
    tfidf_features = vectorizer.transform([cleaned_text]).toarray()

    # Combine Features
    combined_features = [avg_sentence_length, complex_word_ratio, compound_sentiment,
                           domain_age, https_status, alexa_rank,
                           number_of_citations, presence_of_errors] + tfidf_features.tolist()[0]

    # Predict
    prediction = model.predict([combined_features])[0]

    return "Fake" if prediction == 1 else "Real"



# --- 5. Training Data (Example) ---

# NOTE: Replace with a larger, more diverse dataset for better accuracy.
fake_news_urls = [
    "https://www.veteranstoday.com/2023/10/26/breaking-source-cia-head-arrested-for-treason-by-us-special-forces/",
    "https://realrawnews.com/2023/10/military-arrests-cdc-director/",
]

real_news_urls = [
    "https://www.bbc.com/news/world-us-canada-67272238",
    "https://www.reuters.com/world/us/us-military-strikes-syria-response-attacks-us-forces-pentagon-2023-10-26/",
]


# --- 6. Main Execution ---

if __name__ == '__main__':
    # 1. Prepare data
    all_urls = fake_news_urls + real_news_urls
    labels = [1] * len(fake_news_urls) + [0] * len(real_news_urls)  # 1 for fake, 0 for real
    texts = [scrape_article(url) for url in all_urls]
    cleaned_texts = [clean_text(text) for text in texts if text]
    labels = labels[:len(cleaned_texts)]

    # 2. Extract TF-IDF features
    tfidf_matrix, vectorizer = create_tfidf_matrix(cleaned_texts)

    # 3. Extract other features and combine
    all_features = []
    for i, url in enumerate(all_urls[:len(cleaned_texts)]):
        avg_sentence_length, complex_word_ratio, compound_sentiment = extract_writing_style_features(cleaned_texts[i])
        domain_age, https_status, alexa_rank = extract_source_credibility_features(url)
        number_of_citations, presence_of_errors = extract_factual_accuracy_features(cleaned_texts[i], url)

        combined_features = [avg_sentence_length, complex_word_ratio, compound_sentiment,
                               domain_age, https_status, alexa_rank,
                               number_of_citations, presence_of_errors] + tfidf_matrix[i].toarray().tolist()[0]
        all_features.append(combined_features)

    # 4. Train model
    model = train_model(all_features, labels)

    # 5. Example prediction
    test_url = "https://www.bbc.com/news/world-us-canada-67272238"  # Replace with a URL you want to test
    prediction = predict_fake_news(test_url, model, vectorizer)
    print(f"The article at {test_url} is predicted to be: {prediction}")