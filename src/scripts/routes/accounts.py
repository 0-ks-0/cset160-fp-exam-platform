@app.route("/accounts/", methods = [ "GET", "POST"])
def view_accounts():
	if not validate_session(session):
		destroy_session(session)
		return redirect("/login")

	page = request.args.get("page")
	per_page = request.args.get("per_page")

	accounts, page, per_page, min_page, max_page = get_data('users', page, per_page)

	return render_template(
		"accounts.html",
		accounts = accounts,
		page = page,
		per_page = per_page,
		min_page = min_page,
		max_page = max_page
	)

@app.route("/accounts/view/<student_id>", methods = [ "GET" ])
def view_account_info(student_id):
	assignment_data = []

	titles = get_query_rows(f"""
		select `title` from `assignments`
		where id in
			(
				select `assignment_id`
				from `assignment_attempts`
				where `student_id` = {student_id}
			);
		""")

	grades = []

	assignment_attempts_ids = get_query_rows(f"""
		select 	`id` from `assignment_attempts`
		where `student_id` = {student_id}
	""")

	for i in range(len(assignment_attempts_ids)):
		attempt_id = assignment_attempts_ids[i].id

		grade = get_grade(attempt_id)

		grades.append(grade)

	if len(titles) > 0:
		assignment_data.append(titles)
	if len(grades) > 0:
		assignment_data.append(grades)

	# print(titles)
	# print(grades)
	# print(assignment_data)

	return render_template("account_info.html", assignment_data = assignment_data)
