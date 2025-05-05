
# File Share App

Simple anonymous file sharing app.

## Features

- Upload a file → get a code → share code → download file.
- Expiration options: 1h / 12h / 24h.
- Files auto-delete after download or expiration.
- Clean Bootstrap UI with copy-to-clipboard.

## Run locally

```
pip install -r requirements.txt
python app.py
```

## Deploy on Render

- Create a new Web Service → connect this repo → use `python app.py` as start command.
