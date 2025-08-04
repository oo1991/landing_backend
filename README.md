# Landing Backend

This project provides a simple Flask server to store a Mailchimp API key and subscribe emails.

## Endpoints

- `POST /api_key` – Save a Mailchimp API key and list ID. JSON body must contain `api_key` and `list_id`.
- `POST /subscribe` – Subscribe an email using the stored API key.
- `POST /unsubscribe` – Remove an email from the mailing list.
- `POST /status` – Return the current subscription status for an email.
- `GET /snapshot` – Proxy snapshot data and truncate numeric values to two decimals. If the upstream service is unreachable, returns zeros for all fields.

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

## Deploying as a systemd Service

1. Copy `deployment/landing-backend.service` to `/etc/systemd/system/` on your server.
2. Update `WorkingDirectory` and `ExecStart` if your code lives elsewhere.
3. Reload systemd and enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now landing-backend
```

After the service is configured, the GitHub Actions workflow can restart it after copying files.
