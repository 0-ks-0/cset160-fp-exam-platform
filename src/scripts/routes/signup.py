@app.route("/signup/", methods = [ "GET", "POST" ])
def signup():
	destroy_session(session) # Log them out

	if request.method == "POST":
		# No input sanitization? Rock on!
		email_address = request.form.get("email_address")
		password = request.form.get("password") # Not encrypted during transit oh well
		password_verify = request.form.get("password_verify")

		if password != password_verify:
			return render_template(
				"signup.html",
				no_navbar = True,
				error = "Passwords don't match"
			)

		if user_exists(email_address):
			return render_template(
				"signup.html",
				no_navbar = True,
				error = "A user with this email already exists!"
			)

		try:
			run_query(
				"insert into `users` values ( NULL, :first_name, :last_name, :email_address, :password )",

				{
					"first_name": request.form.get("first_name"),
					"last_name": request.form.get("last_name"),
					"email_address": email_address,
					"password": sha_string(password),
				}
			)

			# Insert into students or teachers table
			account_type = request.form.get("account_type")
			if not account_type in ("students", "teachers"):
				raise Exception("Invalid account type")

			run_query(f"insert into `{account_type}` values ( NULL, {user_exists(email_address)} )")

			sql.commit()

			return redirect("/login")
		except:
			return render_template(
				"signup.html",
				no_navbar = True,
				error = "Failed to create account. Contact an administrator."
			)
	else:
		return render_template("signup.html", no_navbar = True)
