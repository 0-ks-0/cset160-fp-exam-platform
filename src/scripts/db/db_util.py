def run_query(query, parameters = None):
	return sql.execute(text(query), parameters)

def run_file(path, parameters = None):
	path = (EXECUTING_DIRECTORY / path).resolve()

	file = open(path)

	return run_query(file.read(), parameters)

def raw_get_query_rows(query_result):
	if not query_result:
		return []

	better_rows = []

	for row in query_result:
		better_rows.append(row._mapping)

	return better_rows

def get_query_rows(query, parameters = None):
	query_result = run_query(query, parameters)
	if not query_result: return []

	return raw_get_query_rows(query_result.all())

def mapping_to_list(rows):
	# result = [dict(row) for row in rows]
	print(f"rows")
	for row in rows:
		print(row)
		row = dict(row)

	return result
