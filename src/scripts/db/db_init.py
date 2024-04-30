run_file("./db/drop.sql")
run_file("./db/tables.sql")

run_query("""
	insert into `users` values
	(
		NULL,
		'Student',
		'Account',
		's@s.s',
		'043a718774c572bd8a25adbeb1bfcd5c0256ae11cecf9f9c3f925d0e52beaf89'
	);
""")

run_query("""
	insert into `students` values
	(
		NULL,
		1
	);
""")

run_query("""
	insert into `users` values
	(
		NULL,
		'Teacher',
		'Account',
		't@t.t',
		'e3b98a4da31a127d4bde6e43033f66ba274cab0eb7eb1c70ec41402bf6273dd8'
	);
""")

run_query("""
	insert into `teachers` values
	(
		NULL,
		2
	);
""")

sql.commit()
