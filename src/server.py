from flask import Flask, redirect, render_template, request, session
from sqlalchemy import create_engine, text

from pathlib import Path
import secrets
from hashlib import sha256

EXECUTING_DIRECTORY = Path(__file__).parent.resolve()

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

def run_query(query, parameters = None):
	return sql.execute(text(query), parameters)

def run_file(path, parameters = None):
	path = (EXECUTING_DIRECTORY / path).resolve()

	file = open(path)

	return run_query(file.read(), parameters)

# Set up database
run_file("./scripts/db/setup.sql")


# Functions
def get_query_rows(query, parameters = None):
	results = run_query(query, parameters)

	if not results:
		return []

	results = results.all()

	list_rows = []

	for row in results:
		list_rows.append(row._mapping)

	return list_rows

# Check if account exists
def user_exists(user_id):
	"""
	:param int user_id:

	:return:
		True if the account associated with the user_id exists

		False otherwise

	:rtype: bool
	"""

	account = get_query_rows(f"select * from `users` where `id` = {user_id}")


	return len(account) < 1

# End of check if account exists

# Login check for email address
def check_user_email(email_address):
	"""
	:param str email_address: The email associated with a user

	:return:
		The user id if the user account exists

		False otherwise

	:rtype:
		int if the email exists

		bool otherwise

	"""

	user = get_query_rows(f"select * from `users` where `email_address` = '{email_address}'")

	if len(user) < 1:
		return False

	return user[0].id


# Create test accounts
def create_user_account(account_type, first_name, last_name, email_address, password):
	if account_type not in ("student", "teacher"):
		return

	if check_user_email(email_address):
		print("Duplicate email address")
		return

	run_query(f"""
		insert into `users`
		values
		(
		   null,
		   '{first_name}',
		   '{last_name}',
		   '{email_address}',
		   '{sha_hash(password)}',
		   '{account_type}'
		);
	""")

	sql.commit()

# Sessions
def destroy_session(session):
	"""
	Destroys the session if it exists
	:param session:

	:return:
		False if session does not exist

		Nothing otherwise
	"""

	if not session:
		return False

	if session.get("user_id"):
		del session["user_id"]

	if session.get("email_address"):
		del session["email_address"]

def validate_session(session):
	"""
	:param session:

	:return:
		True if email is correct for user

		False otherwise

	:rtype: bool
	"""

	if not session:
		return False

	user_id = session.get("user_id")
	email_address = session.get("email_address")

	if not user_id or not email_address:
		return False

	return user_id == check_user_email(email_address)

# End of sessions

# Login Validation
def sha_hash(s):
	return sha256(s.encode("utf-8")).hexdigest()

def validate_email_login(email, password):
	"""
	Checks if the password matches the stored password associated with email

	:param email:
	:param password:

	:return:
		True if the password matches the stored password associated with email

		False otherwise

	:rtype: bool
	"""

	if not check_user_email(email):
		return False

	stored_password = get_query_rows(f"select `password` from `users` where `email_address` = '{email}'")

	if len(stored_password) < 1:
		return False

	stored_password = stored_password[0].password.decode("utf-8")
	return sha_hash(password) == stored_password

# Get email address
def get_email(user_id):
	"""
	:param int user_id:

	:return:
	The email associate with the user_id if the account exists

	False otherwise

	:rtype:
	str if the account exists

	bool otherwise
	"""

	email = get_query_rows(f"select `email_address` from `users` where `id` = {user_id}")

	if len(email) < 1:
		return False

	return email[0].email_address

# End of get email addresss

# Get account type
def get_account_type(user_id):
	"""
	:param user_id:

	:return:
		"teacher" or "student" if the user_id exists

		None otherwise

	:rtype:
		str if the user_id exists
	"""

	user = get_query_rows(f"select `account_type` from `users` where `id` = {user_id};")

	if len(user) < 1:
		return

	return user[0].account_type

# End of get account type

# End of accounts

# Assignments
# Assignments
def create_assignment(user_id, title, points):
	"""
	:return:
		assignment id
	"""
	run_query(f"insert into `assignments` values ( null, {user_id}, '{title}', {points});")

	sql.commit()

	return get_query_rows("select last_insert_id() as `id`;")[0].id

def add_questions(assignment_id, questions):
	"""
	:param int/str assignment_id:
	:param list questions:
	"""

	for question in questions:
		run_query(f"insert into assignment_questions values (null, {assignment_id}, '{question}');")

	sql.commit()

# End of functions

# Insert test data
create_user_account("student", "student", "account", "s@s.s", "s")
create_user_account("teacher", "teacher", "account", "t@t.t", "t")
create_assignment(1, "tests asisgnweoigfjaew", 10)
add_questions(1, ["q1", "q2"])
# End of inserting test values

# Routes
# Home route
@app.route("/")
@app.route("/home/")
def home():
	if not validate_session(session):
		destroy_session(session)
		return redirect("/login")

	return render_template("home.html", account_type = session.get("account_type"))

# Login route
@app.route("/login/")
def create_login():
	destroy_session(session)

	return render_template("login.html", no_navbar = True)

@app.route("/login/", methods=[ "POST" ])
def check_login():
	email = request.form.get("email")
	password = request.form.get("password")

	# Check if username or email exists
	user_id = check_user_email(email)

	if not user_id:
		return render_template(
			"login.html",
			message = "This username or email does not exist",
			no_navbar = True
		)

	# Check login through email
	if validate_email_login(email, password):
		session["user_id"] = user_id
		session["email_address"] = get_email(user_id)
		session["account_type"] = get_account_type(user_id)

	else:
		return render_template(
			"login.html",
			message = "Incorrect password",
			no_navbar = True
		)

	return redirect("/home")


# Sign up route
@app.route("/signup/")
def create_signup():
	destroy_session(session)

	return render_template("signup.html", no_navbar = True)

@app.route("/signup/", methods = [ "POST" ])
def check_signup():
	email_address = request.form.get("email_address")
	password = request.form.get("password")
	password_confirm = request.form.get("password_confirm")

	# Check if passwords match
	if password != password_confirm:
		return render_template(
			"signup.html",
			no_navbar = True,
			message = "Passwords do not match"
		)

	# Check if account with that email address exists
	if check_user_email(email_address):
		return render_template(
			"signup.html",
			no_navbar = True,
			message = "An account with that email addresss already exists"
		)

	first_name = request.form.get("first_name")
	last_name = request.form.get("last_name")

	# Insert into users table
	try:

		account_type = request.form.get("account_type")

		run_query(f"""
			insert into `users`
			values
			(
				null,
				'{first_name}',
				'{last_name}',
				'{email_address}',
				'{sha_hash(password)}',
				'{account_type}'
			);
		""")

		sql.commit()

		return redirect("/login")

	except:
		return render_template(
			"signup.html",
			no_navbar = True,
			message = "Sorry, your account could not be created"
		)

# Accounts
@app.route("/accounts/")
def show_accounts():
	if not validate_session(session):
		destroy_session(session)
		return redirect("/login")

	accounts = get_query_rows(f"select `id`, `email_address` from `users` order by `id`;")

	return render_template(
		"accounts.html",
		accounts = accounts
	)

@app.route('/accounts/<id>')
def view_info(id):
	try:
		user = get_query_rows(f"SELECT * FROM users WHERE id = {id}")[0]

		return render_template('account_info.html',user=user, id=id)

	except Exception as e:
		return str(e)

# Assignments
@app.route("/assignments/")
def show_assignments():
	if not validate_session(session):
		destroy_session(session)
		return redirect("/login")

	assignments = get_query_rows(f"select * from assignments;")

	return render_template(
		"assignments.html",
		account_type = session.get("account_type"),
		assignments = assignments
	)

@app.route("/assignments/create/")
def show_create_assignment():
	if not validate_session(session):
		destroy_session(session)
		return redirect("/login")

	if get_account_type(session.get("user_id")) != "teacher":
		return redirect("/assignments")

	return render_template("assignment_create.html")

@app.route("/assignments/create/", methods = [ "POST" ])
def route_create_assignment():
	if not validate_session(session):
		destroy_session(session)
		return redirect("/login")

	data = request.get_json()

	title = data.get("title")
	points = data.get("points")

	assignment_id = create_assignment(session.get("user_id"), title, points)

	questions = data.get("questions")

	add_questions(assignment_id, questions)

	return {
		"message": "Assignment created sucessfully",
		"url": "/assignments"
	}


@app.route("/take_test/<id>")
def take_test(id):
	questions = get_query_rows(f"select * from `assignment_questions` where `assignment_id` = {id};")

	return render_template(
		"assignment_take.html",
		questions = questions
	)
# End of routes

if __name__ == "__main__":
	app.run()
