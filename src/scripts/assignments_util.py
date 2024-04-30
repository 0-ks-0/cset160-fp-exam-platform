def insert_assignment(teacher_id, title, due_date):
	run_query(f"""
		insert into `assignments`
		values(
		   null,
		   {teacher_id},
		   '{title}',
		   '{due_date}'
		);
	""")

	sql.commit()
