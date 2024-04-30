function set_query_parameters(parameters)
{
	const current_parameters = URLSearchParams(window.location.search)

	for (const [key, value] of parameters)
		current_parameters.set(key, value)

	window.location.search = current_parameters.toString()
}
