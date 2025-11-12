# transcriptsongs

shazam for dj sets. auto-generates timestamped tracklists.

## setup

```bash
pyenv install 3.12.8
/Users/shadrack/.pyenv/versions/3.12.8/bin/python3 -m venv venv
source venv/bin/activate
pip install shazamio requests flask python-dotenv
```

## run

web:
```bash
source venv/bin/activate
python3 app.py
```
http://localhost:5001

cli:
```bash
python3 test_shazam.py your_mix.mp3 90
```

## output

```
0:00 - 1:35 - Brent Faiyaz - Rehab (Winter in Paris)
1:36 - 2:50 - Cash Cobain & BunnaB - Hoes Be Mad
2:51 - 4:21 - Summer Walker - Deep
```
