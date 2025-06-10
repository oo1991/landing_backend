import json
import os
from flask import Flask, request, jsonify
import requests
import hashlib
from flask_cors import CORS

CONFIG_FILE = os.environ.get('CONFIG_FILE', 'config.json')

app = Flask(__name__)
# CORS(app, resources={                  # ← enable CORS
#     r"/subscribe": {"origins": "http://localhost:5173"},
#     r"/status":  {"origins": "http://localhost:5173"},
#     r"/unsubscribe": {"origins": "http://localhost:5173"},
# })

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f)

def get_subscriber_hash(email):
    """Generate MD5 hash of email address for Mailchimp API"""
    return hashlib.md5(email.lower().encode()).hexdigest()


@app.route('/api_key', methods=['POST'])
def set_api_key():
    data = request.get_json()
    if not data or 'api_key' not in data or 'list_id' not in data:
        return jsonify({'error': 'api_key and list_id required'}), 400
    config = load_config()
    config['api_key'] = data['api_key']
    config['list_id'] = data['list_id']
    save_config(config)
    return jsonify({'status': 'saved'})

@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({'error': 'email required'}), 400

    config = load_config()
    api_key = config.get('api_key')
    list_id = config.get('list_id')
    if not api_key or not list_id:
        return jsonify({'error': 'API key or list id not set'}), 500

    email = data['email']
    subscriber_hash = get_subscriber_hash(email)
    dc = api_key.split('-')[-1]
    # Use the member endpoint with PUT
    url = f'https://{dc}.api.mailchimp.com/3.0/lists/{list_id}/members/{subscriber_hash}'
    payload = {
        'email_address': email,
        'status': 'subscribed'
    }
    auth = ('anystring', api_key)

    response = requests.put(url, auth=auth, json=payload)

    if response.status_code in (200, 201):
        # 201 = new member created, 200 = existing member updated
        return jsonify({'status': 'subscribed'}), 200

    # Otherwise return the Mailchimp error
    try:
        details = response.json()
    except ValueError:
        details = {'message': 'invalid response from Mailchimp'}
    return jsonify({'error': 'Mailchimp error', 'details': details}), 400

@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    print('unsubscribe called')
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({'error': 'email required'}), 400

    config = load_config()
    api_key = config.get('api_key')
    list_id = config.get('list_id')
    if not api_key or not list_id:
        return jsonify({'error': 'API key or list id not set'}), 500

    email = data['email']
    subscriber_hash = get_subscriber_hash(email)
    dc = api_key.split('-')[-1]
    url = f'https://{dc}.api.mailchimp.com/3.0/lists/{list_id}/members/{subscriber_hash}'
    
    payload = {
        'status': 'unsubscribed'
    }
    auth = ('anystring', api_key)
    response = requests.patch(url, auth=auth, json=payload)

    if response.status_code == 200:
        return jsonify({'status': 'unsubscribed'}), 200

    # Check if member doesn't exist
    try:
        error_details = response.json()
        if error_details.get('title') == 'Resource Not Found':
            return jsonify({'error': 'Email not found in list'}), 404
    except Exception as e:
        print("JSON decode error or unexpected format:", e)

    return jsonify({'error': 'Mailchimp error', 'details': response.json()}), 400


@app.route('/status', methods=['POST'])
def get_status():
    """Get subscription status of an email"""
    print('status check called')
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({'error': 'email required'}), 400

    config = load_config()
    api_key = config.get('api_key')
    list_id = config.get('list_id')
    if not api_key or not list_id:
        return jsonify({'error': 'API key or list id not set'}), 500

    email = data['email']
    subscriber_hash = get_subscriber_hash(email)
    dc = api_key.split('-')[-1]
    url = f'https://{dc}.api.mailchimp.com/3.0/lists/{list_id}/members/{subscriber_hash}'
    
    auth = ('anystring', api_key)
    response = requests.get(url, auth=auth)

    if response.status_code == 200:
        member_info = response.json()
        return jsonify({
            'email': member_info['email_address'],
            'status': member_info['status']
        }), 200

    # Check if member doesn't exist
    try:
        error_details = response.json()
        if error_details.get('title') == 'Resource Not Found':
            return jsonify({'error': 'Email not found in list'}), 404
    except Exception as e:
        print("JSON decode error or unexpected format:", e)

    return jsonify({'error': 'Mailchimp error', 'details': response.json()}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=38291, debug=True)
