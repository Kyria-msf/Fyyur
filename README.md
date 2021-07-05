# Kyria

## Introduction

Kyria is a musical venue and artist booking site that facilitates the discovery and bookings of shows between local performing artists and venues. This site lets you list new artists and venues, discover them, and list shows with artists as a venue owner.

## Tech Stack (Dependencies)

Our tech stack will include the following:

- **SQLAlchemy** ORM to be our ORM library of choice
- **PostgreSQL** as our database of choice
- **Python3** and **Flask** as our server language and server framework
- **Flask-Migrate** for creating and running schema migrations
- **HTML**, **CSS**, and **Javascript** with **Bootstrap3**for our website's frontend

> **Note** - If I do not mention the specific version of a package, then the default latest stable package will be installed.

## Main Files: Project Structure

```sh
├── README.md
├── app.py *** the main driver of the app.
                  "python app.py" to run after installing dependencies
├── config.py *** Database URLs, CSRF generation, etc
├── error.log
├── forms.py ***  Forms
├── requirements.txt *** The dependencies we need to install with "pip3 install -r requirements.txt"
├── static
│   ├── css
│   ├── font
│   ├── ico
│   ├── img
│   └── js
└── templates
    ├── errors
    ├── forms
    ├── layouts
    └── pages
```

## Development Setup

First, [install Flask](https://flask.palletsprojects.com/en/1.0.x/installation/#install-flask) if you have not already.

```
 cd ~
 pip3 install Flask
```

To start and run the local development server the following must be install:

1. **Initialize and activate a virtualenv using:**

```
cd YOUR_PROJECT_DIRECTORY_PATH/
python -m virtualenv env
source env/Scripts/activate
```

python3 -m venv env

> **Note** - In Unix/macOS, the `env` does not have a `Scripts` directory. Therefore, you'd use the analogous command shown below:

```
source env/bin/activate
```

2. **Install the dependencies:**

```
pip install -r requirements.txt
```

3. **Run the development server:**

```
set FLASK_APP=myapp
set FLASK_ENV=development # enables debug mode
python3 app.py
```

4. **Verify on the Browser**<br>
   Navigate to project homepage [http://127.0.0.1:5000/](http://127.0.0.1:5000/) or [http://localhost:5000](http://localhost:5000)
