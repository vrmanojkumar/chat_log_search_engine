from flask import Flask, render_template, request, jsonify
from datetime import datetime
import spacy
import json
from collections import defaultdict
import re

app = Flask(__name__)

# Load SpaCy model
nlp = spacy.load('en_core_web_sm')

# In-memory storage (replace with database in production)
messages = []
inverted_index = defaultdict(list)

def preprocess_text(text):
    # Tokenize and preprocess text using SpaCy
    doc = nlp(text.lower())
    # Remove stopwords and punctuation, lemmatize
    tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    return tokens

def build_inverted_index():
    global inverted_index
    inverted_index.clear()
    for idx, msg in enumerate(messages):
        tokens = preprocess_text(msg['content'])
        for token in tokens:
            inverted_index[token].append(idx)

def calculate_relevance(query_tokens, message_content):
    """
    Calculate relevance score for a message based on the query tokens.
    This example uses a simple term frequency (TF) approach, 
    but you can replace it with more sophisticated methods like TF-IDF.
    """
    tokens = preprocess_text(message_content)
    score = 0

    # Count term matches (TF)
    for token in query_tokens:
        score += tokens.count(token)

    # Return the score rounded to two decimal places
    return round(score, 2)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add_message', methods=['POST'])
def add_message():
    data = request.json
    message = {
        'id': len(messages) + 1,
        'content': data.get('content'),
        'sender': data.get('sender'),
        'chatroom': data.get('chatroom'),
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    messages.append(message)
    # Update inverted index
    tokens = preprocess_text(message['content'])
    for token in tokens:
        inverted_index[token].append(len(messages) - 1)
    return jsonify(message), 201

@app.route('/search_messages', methods=['GET'])
def search_messages():
    query = request.args.get('query', '').lower()
    sender_filter = request.args.get('sender', '')
    chatroom_filter = request.args.get('chatroom', '')
    date_filter = request.args.get('date', '')

    if not query and not sender_filter and not chatroom_filter and not date_filter:
        return jsonify([])

    # Process query tokens
    query_tokens = preprocess_text(query)
    
    # Get matching message indices from inverted index
    matching_indices = set()
    for token in query_tokens:
        matching_indices.update(inverted_index[token])

    # Filter and rank results
    results = []
    for idx in matching_indices:
        msg = messages[idx]
        
        # Apply filters
        if sender_filter and sender_filter.lower() not in msg['sender'].lower():
            continue
        if chatroom_filter and chatroom_filter.lower() not in msg['chatroom'].lower():
            continue
        if date_filter:
            msg_date = datetime.strptime(msg['timestamp'].split()[0], "%Y-%m-%d")
            filter_date = datetime.strptime(date_filter, "%Y-%m-%d")
            if msg_date.date() != filter_date.date():
                continue

        # Calculate relevance score (simple TF-based approach)
        score = calculate_relevance(query_tokens, msg['content'])
        
        # Highlight matching terms
        highlighted_content = msg['content']
        for token in query_tokens:
            pattern = re.compile(re.escape(token), re.IGNORECASE)
            highlighted_content = pattern.sub(f'<mark>{token}</mark>', highlighted_content)

        result = {
            **msg,
            'relevance_score': score,  # Store the relevance score with 2 decimal places
            'highlighted_content': highlighted_content
        }
        results.append(result)

    # Sort by relevance score
    results.sort(key=lambda x: x['relevance_score'], reverse=True)
    return jsonify(results)

@app.route('/upload_json', methods=['POST'])
def upload_json():
    try:
        file = request.files['file']
        if file:
            data = json.loads(file.read())
            messages.extend(data)
            build_inverted_index()  # Rebuild index after upload
            return jsonify({"message": "File uploaded successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
