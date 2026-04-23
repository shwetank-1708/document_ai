import re
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import os

# Text preprocessing function
def preprocess_text(text: str) -> str:
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation and numbers
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text

# Sample training data (in a real scenario, this would be from actual documents)
invoice_texts = [
    "invoice number 12345 date march 15 2023 total amount 250000 customer john doe",
    "bill of sale invoice 67890 payment due april 30 2023 amount due 150000",
    "tax invoice gst number 123456789 total 50000 including tax",
    "commercial invoice exporter abc company importer xyz corp value 100000",
    "service invoice for consulting services total fee 75000 due date may 1 2023",
    "purchase invoice supplier tech solutions amount 200000 terms net 30",
    "freight invoice shipping charges 25000 destination new york",
    "utility invoice electricity bill for march 2023 total 12000",
    "medical invoice patient bill total charges 85000 insurance covered 60000",
    "hotel invoice guest name jane smith total stay 45000"
]

resume_texts = [
    "john doe software engineer 5 years experience python java javascript",
    "mary smith marketing manager digital marketing seo social media experience",
    "david johnson data scientist machine learning python r statistics phd",
    "sarah wilson project manager agile scrum certification 8 years experience",
    "michael brown sales representative b2b sales crm software experience",
    "lisa davis graphic designer adobe creative suite portfolio website design",
    "robert miller financial analyst excel financial modeling cpa certification",
    "jennifer garcia teacher education masters degree classroom experience",
    "kevin lee chef culinary arts fine dining restaurant management",
    "amy white nurse registered nurse bsn healthcare experience"
]

form_texts = [
    "application form personal information name address phone email",
    "contact form message subject inquiry customer service request",
    "registration form event details participant information payment method",
    "survey form feedback questions rating scale comments section",
    "order form product selection quantity shipping address billing info",
    "membership form application details benefits membership fee",
    "complaint form issue description date location contact information",
    "feedback form satisfaction rating suggestions improvement ideas",
    "subscription form newsletter preferences email frequency content topics",
    "enrollment form course selection student details payment information"
]

# Prepare training data
X = invoice_texts + resume_texts + form_texts
y = ['invoice'] * len(invoice_texts) + ['resume'] * len(resume_texts) + ['form'] * len(form_texts)

# Preprocess all texts
X_processed = [preprocess_text(text) for text in X]

# Train the model
vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
X_vectorized = vectorizer.fit_transform(X_processed)

X_train, X_test, y_train, y_test = train_test_split(X_vectorized, y, test_size=0.2, random_state=42)

classifier = LogisticRegression(random_state=42, max_iter=1000)
classifier.fit(X_train, y_train)

# Evaluate
y_pred = classifier.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model accuracy: {accuracy:.2f}")

# Save the model and vectorizer
model_dir = "app/models"
os.makedirs(model_dir, exist_ok=True)
joblib.dump(vectorizer, os.path.join(model_dir, 'tfidf_vectorizer.pkl'))
joblib.dump(classifier, os.path.join(model_dir, 'document_classifier.pkl'))

print("Model trained and saved successfully!")

# Classification function
def classify_document(text: str) -> str:
    # Load model and vectorizer
    vectorizer = joblib.load('app/models/tfidf_vectorizer.pkl')
    classifier = joblib.load('app/models/document_classifier.pkl')
    
    # Preprocess input text
    processed_text = preprocess_text(text)
    
    # Vectorize
    text_vectorized = vectorizer.transform([processed_text])
    
    # Predict
    prediction = classifier.predict(text_vectorized)[0]
    
    return prediction
