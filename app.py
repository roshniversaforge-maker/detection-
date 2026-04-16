from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import pickle
import os
import sys

# Custom modules
from database.db_config import get_db_connection
from scraper.scraper import extract_reviews
from utils.nlp_preprocess import clean_text
from utils.sentiment_analysis import get_sentiment
from utils.similarity import detect_duplicates

app = Flask(__name__)
app.secret_key = 'super_secret_key_fake_review_detection'

# Model paths
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model')
VEC_PATH = os.path.join(MODEL_DIR, 'tfidf_vectorizer.pkl')
MODEL_PATH = os.path.join(MODEL_DIR, 'svc_model.pkl')

vectorizer = None
model = None

def load_models():
    """Load ML models globally."""
    global vectorizer, model
    try:
        with open(VEC_PATH, 'rb') as f:
            vectorizer = pickle.load(f)
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        print("Models loaded successfully.")
    except Exception as e:
        print(f"Warning: Models not found or failed to load. Run train_model.py first! Error: {e}")

load_models()

# --- AUTHENTICATION ROUTES ---

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db_connection()
        if not conn:
            flash("Database connection error.", "error")
            return render_template('login.html')
            
        try:
            with conn.cursor() as cursor:
                sql = "SELECT id, username, password FROM users WHERE email=%s"
                cursor.execute(sql, (email,))
                user = cursor.fetchone()
                
                if user and user['password'] == password: # In real world, use hashed passwords!
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    return redirect(url_for('dashboard'))
                else:
                    flash("Invalid email or password", "error")
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
        finally:
            conn.close()
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template('signup.html')
            
        conn = get_db_connection()
        if not conn:
            flash("Database connection error.", "error")
            return render_template('signup.html')
            
        try:
            with conn.cursor() as cursor:
                # Check email existence
                cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
                if cursor.fetchone():
                    flash("Email already registered", "error")
                    return render_template('signup.html')
                    
                sql = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
                cursor.execute(sql, (username, email, password))
                flash("Registration successful. Please login.", "success")
                return redirect(url_for('login'))
        except Exception as e:
            flash(f"Server Error: {str(e)}", "error")
        finally:
            conn.close()
            
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        flash(f"If the email {email} exists, a reset link has been sent.", "success")
        return redirect(url_for('login'))
    return render_template('forgot_password.html')

# --- DASHBOARD & API ROUTES ---

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'Please provide a valid product URL.'}), 400
        
    # Check if models are loaded
    if vectorizer is None or model is None:
        return jsonify({'error': 'ML models are not loaded. Please contact administrator.'}), 500
        
    # Step 1: Scrape Reviews
    raw_reviews = extract_reviews(url)
    if not raw_reviews:
        return jsonify({'error': 'Could not extract any reviews from the provided URL.'}), 404
        
    results = []
    genuine_count = 0
    fake_count = 0
    
    # Process reviews
    for text in raw_reviews:
        # Preprocess
        cleaned = clean_text(text)
        
        if not cleaned:  # Skip completely empty after cleaning
            continue
            
        # Transform & Predict
        vec = vectorizer.transform([cleaned])
        pred = model.predict(vec)[0]  # 0 indicates Fake, 1 indicates Genuine
        
        # Sentiment
        sentiment = get_sentiment(text)
        
        label = "Genuine" if pred == 1 else "Fake"
        if label == "Genuine":
            genuine_count += 1
        else:
            fake_count += 1
            
        results.append({
            'text': text,
            'prediction': label,
            'sentiment': sentiment,
            'is_duplicate': False # Will be updated in next step
        })
        
    # Step 2: Duplicate / Similarity check
    results = detect_duplicates(results)
    
    # (Optional) Store analysis into DB
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO reviews (product_url, review_text, prediction, sentiment) VALUES (%s, %s, %s, %s)"
                for r in results:
                    # Truncate text if it's too long just in case
                    db_text = r['text'][:400]
                    cursor.execute(sql, (url, db_text, r['prediction'], r['sentiment']))
        except Exception as e:
            print(f"Failed to store in DB: {e}")
        finally:
            conn.close()
            
    # Calculate percentages
    total = genuine_count + fake_count
    genuine_pct = (genuine_count / total * 100) if total > 0 else 0
    fake_pct = (fake_count / total * 100) if total > 0 else 0
    
    return jsonify({
        'reviews': results,
        'total': total,
        'genuine_count': genuine_count,
        'fake_count': fake_count,
        'genuine_pct': round(genuine_pct, 2),
        'fake_pct': round(fake_pct, 2)
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
