# pm-thinkpieces
Search for thinkpieces across many PM publications

## Running

I'm using `pipenv` to manage virtual environments. Run

```
pipenv --python 3.9
```

To create a virtual environment. Then do

```
pipenv install
```

To install requirements. Then run

```
pipenv shell
```

to set up a virtual environment. Finally, to start Flask, do

```
export FLASK_APP=app.py; flask run
```

Then just open to `127.0.0.1:5000` to start working.


## Versions

Use Python 3.9, or at least update the `runtime.txt` to match your local version.
That ensures that the Python running on Heroku is the same that you're using.
