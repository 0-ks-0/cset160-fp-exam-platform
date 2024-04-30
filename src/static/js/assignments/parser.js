import { Assignment } from "./assignment.js"
import { QUESTION_TYPE, Question } from "./question.js"
import { QuestionOption } from "./question_option.js"

export function sql_to_js(data)
{
	const questions = data.get("questions") || []
	const questionOptions = data.get("question_options") || {}

	const assignment = new Assignment(data)
	assignment.m_Questions = questions.map((rawQuestion) =>
	{
		const question = new Question(rawQuestion)

		const options = []
		const rawOptions = questionOptions[question.getID()]

		if (rawOptions)
			options = rawOptions.map(option => new QuestionOption(option))

		question.m_Options = options

		return question
	})

	return assignment
}

export function js_to_sql(assignment)
{
	// Basic information
	const assignmentData = {}
	assignmentData.id = assignment.getID()
	assignmentData.title = assignment.getTitle()
	assignmentData.due_date = assignment.getDueDate()

	// Questions
	assignmentData.questions = []

	for (const question of assignment.getQuestions())
	{
		const questionData = {}
		questionData.text = question.getText()
		questionData.type = QUESTION_TYPE.translateValue(question.getType())
		questionData.points = question.getPoints()

		// Options
		questionData.options = []

		for (const option of question.getOptions())
		{
			const optionData = {}
			optionData.text = option.getText()
			optionData.is_correct = option.getCorrect()

			questionData.options.push(optionData)
		}

		assignmentData.questions.push(questionData)
	}

	return assignmentData
}
