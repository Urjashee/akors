#### Install requirements
```
uv pip install -r requirements.txt
```

#### Migrate tables
```text
uv run manage.py makemigrations accounts
uv run manage.py migrate
```

#### Run application
```text
uv run manage.py runserver
```