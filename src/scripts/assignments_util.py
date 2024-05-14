def insert_assignment(teacher_id, title, due_date):
	if not due_date:
		due_date = "null"
	else:
		due_date = due_date.replace("T", " ") + ":59"
		due_date = f"'{due_date}'"

	run_query(f"""
		insert into `assignments`
		values(
		   null,
		   {teacher_id},
		   '{title}',
		   {due_date}
		);
	""")

	sql.commit()
