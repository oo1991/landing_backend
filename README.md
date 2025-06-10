# Landing Backend

This project provides a simple Flask server to store a Mailchimp API key and subscribe emails.

## Endpoints

- `POST /api_key` – Save a Mailchimp API key and list ID. JSON body must contain `api_key` and `list_id`.
- `POST /subscribe` – Subscribe an email using the stored API key.
- `POST /unsubscribe` – Remove an email from the mailing list.
- `POST /status` – Return the current subscription status for an email.

## Running the server

Install dependencies and start the app:

```bash
pip install -r requirements.txt
python app.py
```
The application stores the API key and list ID in `config.json` by default. You
can override this location by setting the `CONFIG_FILE` environment variable
before starting the server.

## Tests

Run unit tests with:

```bash
pytest
```
