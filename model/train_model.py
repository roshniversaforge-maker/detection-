import pandas as pd
import numpy as np
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import sys

# Append parent dir
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.nlp_preprocess import clean_text

def generate_dummy_data():
    """
    Generates a realistic dummy dataset for Fake Product Reviews.
    Label 0: Fake Review
    Label 1: Genuine Review
    """
    genuine_reviews = [
        "This product is amazing! It works exactly as described.",
        "Very good quality, I am satisfied with this purchase.",
        "Delivery was quick and the item was nicely packaged.",
        "Not bad for the price, but could be better.",
        "I love this! Have been using it for a week without issues.",
        "Product looks good. The material is premium.",
        "Decent product, matches the description online.",
        "Excellent support from the seller. I highly recommend it.",
        "Great value for money.",
        "Very bad product, broke on the first day.", # Genuine negative
        "The battery life is terrible, I regret buying it.", # Genuine negative
        "Fantastic finish and great utility. A must buy."
    ] * 50 # Duplicate to increase size

    fake_reviews = [
        "best product ever best product ever best product ever",
        "good good good good good good",
        "i like it please buy",
        "100% genuine guaranteed absolutely mind blowing wow",
        "A+++++ seller great item",
        "Very nice, very nice, very nice.",
        "buy this now buy this now",
        "Review in exchange for discount. Product is perfectly flawlessly amazing.",
        "excellent excellent excellent excellent",
        "I didn't buy it but it looks amazing 5 stars!",
        "superb superb superb",
        "amazing item, completely transformed my entire life magically!!"
    ] * 50

    reviews = genuine_reviews + fake_reviews
    labels = [1] * len(genuine_reviews) + [0] * len(fake_reviews)
    
    df = pd.DataFrame({'review': reviews, 'label': labels})
    
    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    return df

def train_and_save_model():
    print("Generating dummy data...")
    df = generate_dummy_data()
    
    print("Cleaning text...")
    df['clean_review'] = df['review'].apply(clean_text)
    
    X = df['clean_review']
    y = df['label']
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # TF-IDF Vectorization
    print("Vectorizing...")
    vectorizer = TfidfVectorizer(max_features=5000)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # Train SVC
    print("Training Support Vector Classifier...")
    svc_model = SVC(kernel='linear', probability=True)
    svc_model.fit(X_train_vec, y_train)
    
    # Evaluate
    y_pred = svc_model.predict(X_test_vec)
    acc = accuracy_score(y_test, y_pred)
    print(f"SVC Accuracy: {acc*100:.2f}%")
    
    # Train XGBoost (Bonus/alternative)
    print("Training XGBoost Classifier...")
    xgb_model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    xgb_model.fit(X_train_vec, y_train)
    xgb_pred = xgb_model.predict(X_test_vec)
    xgb_acc = accuracy_score(y_test, xgb_pred)
    print(f"XGBoost Accuracy: {xgb_acc*100:.2f}%")
    
    # Save the best models and vectorizer
    model_dir = os.path.dirname(os.path.abspath(__file__))
    
    vec_path = os.path.join(model_dir, 'tfidf_vectorizer.pkl')
    model_path = os.path.join(model_dir, 'svc_model.pkl')
    
    with open(vec_path, 'wb') as f:
        pickle.dump(vectorizer, f)
        
    with open(model_path, 'wb') as f:
        pickle.dump(svc_model, f)
        
    print("Models saved successfully to:", model_dir)

if __name__ == "__main__":
    train_and_save_model()
