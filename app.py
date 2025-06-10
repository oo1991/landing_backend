import json
import os
from flask import Flask, request, jsonify
import requests

CONFIG_FILE = os.environ.get('CONFIG_FILE', 'config.json')

app = Flask(__name__)


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f)


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
    dc = api_key.split('-')[-1]
    url = f'https://{dc}.api.mailchimp.com/3.0/lists/{list_id}/members'
    payload = {
        'email_address': email,
        'status': 'subscribed'
    }
    auth = ('anystring', api_key)
    response = requests.post(url, auth=auth, json=payload)
    if response.status_code in (200, 201):
        return jsonify({'status': 'subscribed'}), 200
    return jsonify({'error': 'Mailchimp error', 'details': response.json()}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
