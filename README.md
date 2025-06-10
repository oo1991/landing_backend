# Landing Backend

This project provides a simple Flask server to store a Mailchimp API key and subscribe emails.

## Endpoints

- `POST /api_key` – Save a Mailchimp API key and list ID. JSON body must contain `api_key` and `list_id`.
- `POST /subscribe` – Subscribe an email using the stored API key.

## Running the server

Install dependencies and start the app:

```bash
pip install -r requirements.txt
python app.py
```

## Tests

Run unit tests with:

```bash
pytest
```
