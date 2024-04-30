# Imports
from pathlib import Path
import hashlib
import json
import math
import secrets

from flask import Flask, redirect, render_template, request, session, send_file, url_for
from sqlalchemy import create_engine, text

SERVER_DIRECTORY = Path(__file__).parent.resolve()
EXECUTING_DIRECTORY = SERVER_DIRECTORY

# Initialize Flask
app = Flask(__name__)
app.secret_key = secrets.token_hex()

# Connect to database
DB_USERNAME = "root"
DB_PASSWORD = "1234"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_DB = "cset160final"

engine = create_engine(f"mysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DB}")
sql = engine.connect()

# The rest
def load_file(path):
	global EXECUTING_DIRECTORY

	path = (EXECUTING_DIRECTORY / path).resolve()

	ORIGINAL_EXECUTING_DIRECTORY = EXECUTING_DIRECTORY
	EXECUTING_DIRECTORY = Path(path).parent.resolve()

	try:
		file = open(path)

		exec(file.read(), globals())

		file.close()
	except Exception as error:
		print(error)
		pass

	EXECUTING_DIRECTORY = ORIGINAL_EXECUTING_DIRECTORY

load_file("./scripts/db_util.py")
load_file("./scripts/user_util.py")
load_file("./scripts/functions.py")
load_file("./scripts/routes.py")
load_file("./scripts/db_init.py")

# Brap you
if __name__ == "__main__":
 	app.run()
