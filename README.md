# Match backend


## Set up


### Prerequisites
- Python 3.11 is mandatory
- Install virutalenv (`pip install virtualenv`)
- Install postgres15. Download Postgres.app (https://postgresapp.com/) and via Homebrew with `brew install postgresql@15` source: `https://www.postgresql.org/download/macosx/`


### Setting up and running the backend

1) Create a virtual environment in the root project folder:

```virtualenv .venv```

2) Activate the virutal environment:

```source .venv/bin/activate```

3) Install pip-tools

```python -m pip install pip-tools```

4) Install all the packages in the venv (.venv):

```pip install -r requirements.txt```

5) Create a new Server in the Postgres.app in the left-bottom of the application with a +

6) Add match-backend to the name of that new server and start it.

7) In terminal, in the root folder of your project with the env activated, run the migrations

```python manage.py migrate```

8) Now, with everything running (postgresql server and migrations applied), run the django server

```python manage.py runserver```


### Extra: Adding new packages

If you want to add new packages:

1) Add the name of the package (can be with its specific version) in `requirements.in`
2) Run `pip-compile requirements.in` and `requirements.txt` will be updated automatically.
3) Activate the venv.
4) Run `pip install -r requirements.txt` to install new or updated packages.
