function createQuestion()
{
	const question = document.createElement("input")
	question.setAttribute("type", "text")
	question.name = "question"
	question.placeholder = "Question"
	question.required = true

	const add_button = document.querySelector("#question_create_button")

	const form = document.querySelector("#question_create_form")

	form.insertBefore(question, add_button)
}

function createAssignment(event)
{
	event.preventDefault()

	const form = document.querySelector("#question_create_form")

	const form_data = new FormData(form)

	const questions = document.getElementsByName("question")

	const questions_data = []

	for (let i = 0; i < questions.length; i++)
	{
		questions_data.push(questions[i].value)
	}

	fetch("/assignments/create", {
		headers:
		{
			"Content-Type" : "application/json"
		},
		method: "POST",
		body: JSON.stringify
		({
			"title": form_data.get("title"),
			"points": form_data.get("points"),
			"questions": questions_data
		})
	})
	.then(function (response) // Callback function when response sent from server
	{
		// Check if status code between 200 and 300
		if (response.ok)
		{
			return response.json() // Convert response from server to json

			.then(response =>
			{
				alert(response.message)

				top.location = response.url
			})
		}
		else
		{
			throw Error(`Error: ${response.status || response.statusText}`)
		}
	})
	.catch(error => // Catch errors from sending / receiving
	{
		console.log(error)
	})

}

function submitAssignment(event, assignment_id)
{
	event.preventDefault()

	const answers = document.getElementsByClassName("answer")

	const data = []

	for (const answer of answers)
	{
		const name = answer.name

		data.push({
			"question_id":  name.substring(name.indexOf("_") + 1),
			"response": answer.value
		})
	}

	fetch(`/take_test/${assignment_id}`, {
		headers:
		{
			"Content-Type" : "application/json"
		},
		method: "POST",
		body: JSON.stringify({
			"assignment_id": assignment_id,
			"data": data
		})
	})
	.then(function (response) // Callback function when response sent from server
	{
		// Check if status code between 200 and 300
		if (response.ok)
		{
			return response.json() // Convert response from server to json

			.then(response =>
			{
				alert(response.message)

				top.location = response.url
			})
		}
		else
		{
			throw Error(`Error: ${response.status || response.statusText}`)
		}
	})
	.catch(error => // Catch errors from sending / receiving
	{
		console.log(error)
	})
}
