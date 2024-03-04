# Match backend

## Set up

Prerequisites:
- Python 3.11 is mandatory
- Install virutalenv (`pip install virtualenv`)
- Install pip-tools (`python -m pip install pip-tools`)

1) Create a virtual environment in the root project folder:

```virtualenv .venv```

2) Activate the virutal environment:

```source .venv/bin/activate```

3) Install all the packages in the venv (match-venv):

```pip install -r requirements.txt```

## Running the backend

1) With venv activated, execute in one terminal this command to run Django server:

```python manage.py runserver```


### Adding new packages

For installing new packages

1) Add the name of the package (can be with its specific version) in `requirements.in`
2) Run `pip-compile requirements.in` and `requirements.txt` will be updated automatically.
3) Activate the venv.
4) Run `pip install -r requirements.txt` to install new or updated packages.
