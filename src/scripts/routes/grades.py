@app.route("/grades/")
def grades():
	if not validate_session(session):
		destroy_session(session)
		return redirect("/login")

	return render_template("grades.html", account_type = session.get("account_type"))
