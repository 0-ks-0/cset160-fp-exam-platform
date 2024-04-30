def sha_string(string):
	return hashlib.sha256(string.encode("utf-8")).hexdigest()

def user_exists(email_address):
	"""
	:param str email_address: The email associated with a user
	:return: The user id if the user account exists, False otherwise
	:rtype: int if the email exists, bool otherwise
	"""
	user = get_query_rows(f"select * from `users` where `email_address` = '{email_address}'")

	if len(user) < 1:
		return False

	return user[0].id

def get_student_id(user_id):
	"""
	:param int user_id:
	:return: The student id if the student account exists, False otherwise
	:rtype: int if the user_id exists, bool otherwise
	"""

	student = get_query_rows(f"select * from `students` where `user_id` = {user_id}")

	if len(student) < 1:
		return False

	return student[0].id

def get_teacher_id(user_id):
	"""
	:param int user_id:
	:return: The teacher id if the teacher account exists, False otherwise
	:rtype: int if the user_id exists, bool otherwise
	"""

	teacher = get_query_rows(f"select * from `teachers` where `user_id` = {user_id}")

	if len(teacher) < 1:
		return False

	return teacher[0].id

def get_account_type(user_id):
	"""
	:param int user_id:
	:return:
		"student" if the account type is student
		"teacher" if the account type is teacher
		False otherwise
	:rtype:
		str if the account exists
		bool otherwise
	"""

	if get_student_id(user_id):
		return "student"

	if get_teacher_id(user_id):
		return "teacher"

	return False

def validate_login(email_address, password):
	if not user_exists(email_address):
		return False

	stored_password = get_query_rows(f"select `password` from `users` where `email_address` = '{email_address}'")

	if len(stored_password) < 1:
		return False

	stored_password = stored_password[0].password
	stored_password = stored_password.decode("utf-8")

	return sha_string(password) == stored_password

def destroy_session(session):
	if not session:
		return

	if session.get("user_id"): del session["user_id"]
	if session.get("email_address"): del session["email_address"]

def validate_session(session):
	if not session:
		return False

	user_id = session.get("user_id")
	email_address = session.get("email_address")

	if not user_id or not email_address:
		return False

	return user_id == user_exists(email_address)
