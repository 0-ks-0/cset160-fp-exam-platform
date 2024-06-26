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


	return len(account) > 0

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

def delete_assignment(assignment_id):
	# TODO create a deleted assignments table

	run_query(f"delete from `assignments` where `id` = {assignment_id};")

	sql.commit()

# Attempts
def create_assignment_attempt(user_id, assignment_id, submission_date = None, graded = None, grade = None, graded_by = None):
	"""
	:param int/str user_id:
	:param int/str assignment_id:
	:param str/None submission_date:
	:param int/bool/str/None graded:
	:param int/str/None grade:
	:param int/str/None graded_by:

	:return:
		assignment attempt id
	"""

	if not submission_date:
		submission_date = "now()"
	else:
		submission_date = f"'{submission_date}'"

	if not graded:
		graded = "false"
	else:
		graded = "true"

	if not grade:
		grade = "null"

	if not graded_by:
		graded_by = "null"

	run_query(f"""
		insert into `assignment_attempts`
		values
			(
				null,
				{user_id},
				{assignment_id},
				{submission_date},
				{graded},
				{grade},
				{graded_by}
			);
	""")

	sql.commit()

	return get_query_rows("select last_insert_id() as `id`;")[0].id

def create_attempt_response(attempt_id, question_id, response):
	"""
	:param int/str attempt_id:
	:param int/str question_id:
	:param str response:
	"""

	run_query(f"""
		insert into `assignment_attempt_responses`
		values
			(
				null,
				{attempt_id},
				{question_id},
				'{response}'
			);
	""")

	sql.commit()

# Check if user already attempted assignment
def attempt_exists(user_id, assignment_id):
	"""
	:return:
		1 if attempt exists

		0 otherwise
	"""

	return get_query_rows(f"select exists(select * from assignment_attempts where assignment_id = {assignment_id} and user_id = {user_id}) as `exists`;")[0].exists

def assignment_exists(assignment_id):
	data = get_query_rows(f"select * from `assignments` where `id` = {assignment_id};")

	return len(data) > 0

# Get assignment data
def get_assignment_data(assignment_id):
	"""
	{
		"assignment_info" (assignments table),
		"teacher_info" (users table),
		"num_of_students": (int),
		"students": [{
			"user_info" (users table),
			"attempt_info" (assignment_attempts table)
		}]
	}
	"""

	data = {}
	# Make sure assignment exists
	if not assignment_exists(assignment_id):
		return

	# Get info from assignments table
	assignment_info = get_query_rows(f"select * from `assignments` where `id` = {assignment_id};")[0]

	data["assignment_info"] = assignment_info

	teacher_id = assignment_info.user_id

	data["teacher_info"] = get_query_rows(f"select * from `users` where `id` = {teacher_id};")[0]

	data["num_of_students"] = get_query_rows(f"select count(*) as `num` from `assignment_attempts` where `assignment_id` = {assignment_id};")[0].num

	# Get students and their attempt info
	attempts = get_query_rows(f"select * from assignment_attempts where assignment_id = {assignment_id};")

	students = []

	# No attempt data on assignment
	if len(attempts) < 1:
		data["students"] = students

	else:
		user_ids = [a.user_id for a in attempts]

		for user_id in user_ids:
			user_info = get_query_rows(f"select * from `users` where `id` = {user_id};")[0]
			attempt_info = get_query_rows(f"select * from `assignment_attempts` where `assignment_id` = {assignment_id} and user_id = {user_id};")[0]

			students.append({
				"user_info": user_info,
				"attempt_info": attempt_info
				# TODO add email of the teacher for graded_by
			})

		data["students"] = students

	return data

# Get assignments data for user
def get_user_assignment_data(user_id, assignment_id):
	"""
	{
		"assignment_info" (assignments table),
		"attempt_info" (assignment_attempts table),
		"graded_by" (email of teacher or False)

	}
	"""

	data = {}

	if not assignment_exists(assignment_id):
		return data

	if not user_exists(user_id):
		return data

	# Get assignment info
	assignment_info = get_query_rows(f"select * from `assignments` where `id` = {assignment_id};")[0]

	data["assignment_info"] = assignment_info

	# Get attempt info
	attempt_info = get_query_rows(f"select * from `assignment_attempts` where `user_id` = {user_id} and `assignment_id` = {assignment_id};")

	if len(attempt_info) > 0:
		attempt_info = attempt_info[0]

	data["attempt_info"] = attempt_info

	# Get teacher info of the grader
	graded_by = attempt_info.graded_by

	teacher_info = None

	if graded_by:
		teacher_info = get_email(graded_by)

	data["graded_by"] = teacher_info

	return data

# Get questions of assignment
def get_assignment_questions(assignment_id):
	questions = get_query_rows(f"select * from `assignment_questions` where `assignment_id` = 1;")

	return questions

# Update question
def update_question(question_id, question):
	run_query(f"update `assignment_questions` set `question` = '{question}' where `id` = {question_id};")

	sql.commit()

# Get responses to an atttempt
# def get_attempt_responses(attempt_id):
# 	"""
# 	:return:
# 		list of dicts of responses

# 		[] if the attempt_id does not exist
# 	"""
# 	responses = get_query_rows(f"select * from `assignment_attempt_responses` where `attempt_id` = {attempt_id};")

# 	return responses

# Get attempt data
def get_attempt_data(attempt_id):
	"""
	:return:
		list of dicts containing information on each question and response
		[{
			"question_data": {} (assignment_questions table),
			"response_data": {} (assignment_attempt_responses table)
		}]
	"""

	attempt = get_query_rows(f"select * from `assignment_attempts` where `id` = {attempt_id};")

	# Check if attempt_id exists
	if len(attempt) < 1:
		return {}

	# Find questions and responses to assignment
	assignment_id = attempt[0].assignment_id

	responses = get_query_rows(f"select * from `assignment_attempt_responses` where `attempt_id` = {attempt_id};")

	# question_ids in the attempt/assignment
	question_ids = [r.question_id for r in responses]

	data = []

	for question_id in question_ids:
		question_data = get_query_rows(f"select * from `assignment_questions` where `assignment_id` = {assignment_id} and `id` = {question_id};")[0]
		response_data = get_query_rows(f"select * from `assignment_attempt_responses` where `attempt_id` = {attempt_id} and question_id = {question_id};")[0]

		data.append({
			"question_data": question_data,
			"response_data": response_data
		})

	return data

# Update attempt grade
def grade_attempt(attempt_id, grade, graded_by):
	"""
	:param int/str attempt_id:
	:param int/str grade:
	:param int/str graded_by: the user_id
	"""

	run_query(f"update `assignment_attempts` set `graded` = true, `grade` = {grade}, `graded_by` = {graded_by} where `id` = {attempt_id};")

	sql.commit()

# End of functions

# Insert test data
# Accounts
create_user_account("student", "student", "account", "s@s.s", "s")
create_user_account("student", "student2", "account2", "s2@s.s", "s")
create_user_account("teacher", "teacher", "account", "t@t.t", "t")

# Assignments
create_assignment(2, "assignment name test", 10)
add_questions(1, ["q1", "q2"])

create_assignment(2, "assignment 2", 10)
add_questions(2, ["test q1", "test q2"])

# Attempts
attempt_id1 = create_assignment_attempt(1, 1)
create_attempt_response(attempt_id1, 1, "answer 1")
create_attempt_response(attempt_id1, 2, "answer 2")

attempt_id2 = create_assignment_attempt(1, 2)
create_attempt_response(attempt_id2, 1, "attempt 2 answer 1")
create_attempt_response(attempt_id2, 2, "attempt 2 answer 2")

# Grading
grade_attempt(attempt_id2, 2, 2)

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
	if not validate_session(session):
		destroy_session(session)
		return redirect("/login")

	try:
		user = get_query_rows(f"SELECT * FROM users WHERE id = {id}")[0]

		assignments_data = []

		# Find all assignment_ids for user
		attempts = get_query_rows(f"select * from `assignment_attempts` where `user_id` = {id};")

		# Get info for each assignment
		if len(attempts) > 0:
			for attempt in attempts:
				assignment_id = attempt.assignment_id

				assignments_data.append(get_user_assignment_data(id, assignment_id))

		return render_template(
			"account_info.html",
			user = user,
			assignments_data = assignments_data
		)

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

@app.route("/assignments/", methods = [ "DELETE" ])
def route_delete_assignment():
	assignment_id = request.get_json().get("assignment_id")

	delete_assignment(assignment_id)

	return {
		"message": f"Assignment {assignment_id} has been deleted",
		"url": "/assignments"
	}

@app.route("/assignments/<id>")
def view_assignment_info(id):
	if not validate_session(session):
		destroy_session(session)
		return redirect("/login")

	if not assignment_exists(id):
		return redirect("/assignments")

	data = get_assignment_data(id)

	return render_template(
		"assignment_info.html",
		account_type = session.get("account_type"),
		data = data
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

@app.route("/assignments/edit/<id>")
def show_assignment_edit_page(id):
	if not validate_session(session):
		destroy_session(session)
		return redirect("/login")

	# Must be teacher account
	if session.get("account_type") != "teacher":
		return redirect("/login")

	# Make sure assignment exists
	if not assignment_exists(id):
		return redirect("/assignments")

	return render_template(
		"assignment_edit.html",
		assignment_id = id,
		questions = get_assignment_questions(id)
	)

@app.route("/assignments/edit/<id>", methods = [ "PATCH" ])
def route_update_assignment(id):
	question_data = request.get_json()

	for data in question_data:
		update_question(data.get("question_id"), data.get("question"))

	return {
		"message": "Updated successfully",
		"url": "/assignments"
	}

@app.route("/take_test/<id>")
def take_test(id):
	if not validate_session(session):
		destroy_session(session)
		return redirect("/login")

	# Must be student account
	if session.get("account_type") != "student":
		return redirect("/login")

	# Cannot take assignment more than once
	if attempt_exists(session.get("user_id"), id):
		return redirect("/assignments")


	assignment_data = get_query_rows(f"select * from `assignments` where `id` = {id};")

	if len(assignment_data) < 1:
		return redirect("/assignments")

	questions = get_query_rows(f"select * from `assignment_questions` where `assignment_id` = {id};")

	return render_template(
		"assignment_take.html",
		assignment_data = assignment_data[0],
		questions = questions
	)

@app.route("/take_test/<id>", methods = [ "POST" ])
def submit_test(id):
	json = request.get_json()

	assignment_id = json.get("assignment_id")
	data = json.get("data")

	attempt_id = create_assignment_attempt(session.get("user_id"), assignment_id)

	for d in data:
		create_attempt_response(attempt_id, d.get("question_id"), d.get("response"))

	return {
		"message": "Assignment submitted",
		"url": "/assignments"
	}

@app.route("/assignments/grade/<id>")
def show_grading_page(id):
	if not validate_session(session):
		destroy_session(session)
		return redirect("/login")

	# Must be teacher account
	if session.get("account_type") != "teacher":
		return redirect("/login")

	return render_template(
		"assignment_grade.html",
		attempt_id = id,
		attempt_data = get_attempt_data(id)
	)

@app.route("/assignments/grade/<id>", methods = [ "PATCH" ])
def route_grade_attempt(id):
	data = request.get_json()

	earned_points = data.get("earned_points")

	# TODO maybe validate account type as teacher

	attempt = get_query_rows(f"select * from `assignment_attempts` where `id` = {id};")

	assignment_id = attempt[0].assignment_id

	grade_attempt(id, earned_points, session.get("user_id"))

	return {
		"message": "Assignment has been graded",
		"url": f"/assignments/{assignment_id}"
	}

# End of routes

if __name__ == "__main__":
	app.run()
