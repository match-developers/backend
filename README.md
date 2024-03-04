# Match backend

## Set up

Prerequisites: Python 3.11 is mandatory

1) Activate the virtual environment:

```source match-venv/bin/activate```

2) Install all the packages in the venv (match-venv):

```pip install -r requirements.txt```

## Running the backend

1) Execute in one terminal this command to run Django server in the development environment

```python manage.py runserver```


### Adding new packages

For installing new packages

1) Add the name of the package (can be with its specific version) in `requirements.in`
2) Run `pip-compile requirements.in` and `requirements.txt` will be updated automatically.
4) Run `pip install -r requirements.txt` to install new or updated packages.
