@app.route("/assignments/", methods = [ "GET"])
def view_assignments():
	if not validate_session(session):
		destroy_session(session)
		return redirect("/login")

	page = request.args.get("page")
	per_page = request.args.get("per_page")

	assignments, page, per_page, min_page, max_page = get_data('assignments', page, per_page)

	return render_template(
		"assignments.html",
		assignments = assignments,
		page = page,
		per_page = per_page,
		min_page = min_page,
		max_page = max_page
	)

@app.route("/assignments/add/")
def initialize_assignment():
	if not validate_session(session):
		destroy_session(session)
		return redirect("/login")

	run_query(f"""
		insert into `assignments` values
		(
			NULL,
			{session.get("teacher_id")},
			'New Assignment',
			'9999-12-31 00:00:00'
		);
	""")

	assignment_id = get_query_rows("select last_insert_id() as 'id' from `assignments`")
	if len(assignment_id) < 1:
		return redirect("/home") # TODO: Show an error

	return redirect(f"/assignments/edit/{assignment_id[0].id}")

@app.route("/assignments/edit/<assignment_id>")
def add_assignment(assignment_id = 1):
	if not validate_session(session):
		destroy_session(session)
		return redirect("/login")

	# TODO: Make sure it's a teacher account

	# Get basic information
	assignment_data = get_query_rows(f"select * from `assignments` where `id` = {assignment_id}")
	if len(assignment_data) < 1:
		return redirect("/home") # TODO: Show error

	# Get questions
	assignment_questions = get_query_rows(f"select * from `assignment_questions` where `assignment_id` = {assignment_id}")

	# Get question options
	assignment_question_options = {}

	for question in assignment_questions:
		question_id = question.get("id")

		assignment_question_options[question_id] = get_query_rows(f"select * from `assignment_question_options` where `question_id` = {question_id}")

	print(assignment_question_options)
	print(type(assignment_question_options))

	assignment_question_options = mapping_to_list(assignment_question_options)
	print("adsf")
	print(assignment_question_options)
	assignment_question_options = json.dumps(assignment_question_options)
	print("b")
	print(assignment_question_options)

	return render_template(
		"assignment_edit.html",
		assignment_data = assignment_data[0],
		assignment_questions = assignment_questions,
		assignment_question_options = assignment_question_options
	)

@app.route("/assignments/edit/", methods = [ "POST" ])
def update_assignment():
	if not validate_session(session):
		destroy_session(session)
		return redirect("/login")

	teacher_id = session.get("teacher_id") # TODO: Validate this

	assignment_data = request.form.get("assignment_data")
	if not assignment_data:
		return redirect("/home") # TODO: Show error

	assignment_data = json.loads(assignment_data)

	# Basic information
	assignment_id = assignment_data.get("id")
	title = assignment_data.get("title")
	due_date = assignment_data.get("due_date")

	run_query(f"""
		update `assignments`
		set `title` = '{title}',
		`due_date` = '{due_date}'
		where `id` = {assignment_id}
	""")

	# Handle each question
	for question in assignment_data.get("questions"):
		run_query(f"""
			insert into `assignment_questions` values
			(
				NULL,
				{assignment_id},
				'{question.get("text")}',
				'{question.get("type")}',
				{question.get("points")}
			);
		""")

		# TODO: Validate this
		question_id = get_query_rows("select last_insert_id() as 'id' from `assignment_questions`")[0].id

		# Handle each option
		for option in question.get("options"):
			# TODO: Validate success of this
			run_query(f"""
				insert into `assignment_question_options` values
				(
					NULL,
					{question_id},
					'{option.get("text")}',
					{1 if option.get("is_correct") else 0}
				);
			""")

	# TODO: Success?
	sql.commit()

	return redirect("/home")

@app.route("/assignments/view/<assignment_id>", methods = [ "GET" ])
def view_assignment_info(assignment_id):
	if not validate_session(session):
		destroy_session(session)
		return redirect("/login")

	assignment_data = []

	assignment_info = get_assignment_info(assignment_id)

	teacher = get_assignment_teacher(assignment_id)

	students = get_assignment_students(assignment_id)

	grades = []

	# Calculate grade for each student
	for student in students:
		attempt_id = get_attempt_id(student.student_id, assignment_id)

		grade = get_grade(attempt_id)

		grades.append(grade)

	if len(students) > 0:
		assignment_data.append(students)

	if len(grades) > 0:
		assignment_data.append(grades)

	return render_template(
		"assignment_info.html",
		assignment_info = assignment_info,
		teacher = teacher,
		assignment_id = assignment_id,
		account_type = session.get("account_type"),
		students_count = len(students),
		assignment_data = assignment_data
	)

@app.route("/assignments/take/<assignment_id>")
def take_assignment(assignment_id):
	if not validate_session(session):
		destroy_session(session)
		return redirect("/login")

	# TODO: Make sure assignment actually exists

	# Get basic information
	assignment_data = get_query_rows(f"select * from `assignments` where `id` = {assignment_id}")
	if len(assignment_data) < 1:
		return redirect("/home") # TODO: Show error

	# Get questions
	assignment_questions = get_query_rows(f"select * from `assignment_questions` where `assignment_id` = {assignment_id}")

	# Get question options
	assignment_question_options = {}

	for question in assignment_questions:
		question_id = question.get("id")

		assignment_question_options[question_id] = get_query_rows(f"select * from `assignment_question_options` where `question_id` = {question_id}")

	return render_template(
		"assignment_take.html",
		assignment_data = assignment_data[0],
		assignment_questions = assignment_questions,
		assignment_question_options = assignment_question_options
	)
