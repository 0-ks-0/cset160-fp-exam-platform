@app.route("/login/", methods = [ "GET", "POST" ])
def login():
	destroy_session(session)

	if request.method == "POST":
		email_address = request.form.get("email_address")
		password = request.form.get("password")
		user_id = user_exists(email_address)

		if not user_id:
			return render_template(
				"login.html",
				no_navbar = True,
				error = "A user with this email does not exist"
			)

		if validate_login(email_address, password):
			session["user_id"] = user_id
			session["email_address"] = email_address

			account_type = get_account_type(user_id)
			session["account_type"] = account_type

			session["student_id"] = get_student_id(user_id)
			session["teacher_id"] = get_teacher_id(user_id)

			return redirect("/home")
		else:
			return render_template(
				"login.html",
				no_navbar = True,
				error = "Invalid password"
			)
	else:
		return render_template("login.html", no_navbar = True)
