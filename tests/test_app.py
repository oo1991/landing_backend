import sys, pathlib; sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import os
import json
from unittest.mock import patch
from app import app, save_config, CONFIG_FILE


def test_set_api_key(tmp_path, monkeypatch):
    config_file = tmp_path / "config.json"
    monkeypatch.setattr('app.CONFIG_FILE', str(config_file))
    with app.test_client() as client:
        resp = client.post('/api_key', json={'api_key': 'key-us1', 'list_id': '123'})
        assert resp.status_code == 200
        assert config_file.exists()


@patch('app.requests.put')
def test_subscribe_with_mock(mock_put, tmp_path, monkeypatch):
    config_file = tmp_path / "config.json"
    monkeypatch.setattr('app.CONFIG_FILE', str(config_file))
    save_config({'api_key': 'key-us1', 'list_id': '123'})
    mock_put.return_value.status_code = 200
    mock_put.return_value.json.return_value = {}

    with app.test_client() as client:
        resp = client.post('/subscribe', json={'email': 'test@example.com'})
        assert resp.status_code == 200
        mock_put.assert_called()
