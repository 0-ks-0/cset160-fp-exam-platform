@app.route("/assignments/")
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
