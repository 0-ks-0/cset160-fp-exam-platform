// Imports
import { Helper } from "../JSModules/helper.js"

import { sql_to_js, js_to_sql } from "./parser.js"
import { QUESTION_TYPE, Question } from "./question.js"
import { QuestionOption } from "./question_option.js"
import { AssignmentRenderer } from "./renderer.js"

// Globals
const g_Helper = new Helper()
const g_Renderer = new AssignmentRenderer()

var question_display = null
var g_Assignment = null
var g_CurrentQuestionNumber = 0

// Functions
function goToQuestion(index)
{
	g_CurrentQuestionNumber = g_Helper.clamp(index, 0, g_Assignment.getQuestions().length - 1)

	g_Renderer.renderAssignment(g_Assignment, g_CurrentQuestionNumber, question_display, true)

	document.querySelector("#question_number").innerHTML = g_CurrentQuestionNumber + 1
}

function createQuestionData(isCorrect)
{
	const data = new Map()

	data.set("is_correct", isCorrect)

	return data
}

function createDummyQuestion(isCorrect)
{
	return new QuestionOption(createQuestionData(isCorrect))
}

function createQuestion()
{
	const dropdown_question_type = document.querySelector("#dropdown_question_type")

	const questionData = new Map()
	questionData.set("text", "Enter Question Text")
	questionData.set("type", dropdown_question_type.value)

	const question = new Question(questionData)

	// Make some dummy questions
	if (QUESTION_TYPE.lookupValue(dropdown_question_type.value) == QUESTION_TYPE.MULTIPLE_CHOICE)
	{
		question.getOptions().push(createDummyQuestion(true))
		question.getOptions().push(createDummyQuestion())
		question.getOptions().push(createDummyQuestion())
		question.getOptions().push(createDummyQuestion())
	}
	else
		question.getOptions().push(createDummyQuestion(true))

	// Insert it
	g_Assignment.getQuestions().splice(g_CurrentQuestionNumber + 1, 0, question)
	g_CurrentQuestionNumber = g_Assignment.getQuestions().indexOf(question)

	goToQuestion(g_CurrentQuestionNumber)
}

function deleteQuestion()
{
	g_Helper.popFrom(g_Assignment.getQuestion(), g_Assignment.getQuestion(g_CurrentQuestionNumber))

	goToQuestion(g_CurrentQuestionNumber)
}

// Hooks
g_Helper.hookEvent(window, "load", false, () =>
{
	question_display = document.querySelector("#question_display")

	g_Assignment = sql_to_js(g_AssignmentData)
	g_CurrentQuestionNumber = g_Assignment.getQuestion(g_CurrentQuestionNumber)

	// Setup controls
	const input_title = document.querySelector("#input_title")
	const dropdown_due_date = document.querySelector("#dropdown_due_date")
	const btn_previous_question = document.querySelector("#btn_previous_question")
	const btn_next_question = document.querySelector("#btn_next_question")
	const btn_add_question = document.querySelector("#btn_add_question")
	const btn_delete_question = document.querySelector("#btn_delete_question")
	const btn_submit_assignment = document.querySelector("#btn_submit_assignment")

	// Basic information
	g_Helper.hookElementEvent(input_title, "change", true, (_, self) =>
	{
		g_Assignment.setTitle(self.value)
	})

	g_Helper.hookElementEvent(dropdown_due_date, "change", true, (_, self) =>
	{
		// Convert to SQL datetime syntax
		let time = self.value.replace('T', ' ')
		time += ":00"

		g_Assignment.setDueDate(time)
	})

	g_Helper.hookElementEvent(dropdown_due_date, "input", true, (_, self) => // Lazy yeah yeah shush
	{
		// Convert to SQL datetime syntax
		let time = self.value.replace('T', ' ')
		time += ":00"

		g_Assignment.setDueDate(time)
	})

	// Pagers
	g_Helper.hookElementEvent(btn_previous_question, "click", true, () =>
	{
		g_CurrentQuestionNumber--
		goToQuestion(g_CurrentQuestionNumber)
	})

	g_Helper.hookElementEvent(btn_next_question, "click", true, () =>
	{
		g_CurrentQuestionNumber++
		goToQuestion(g_CurrentQuestionNumber)
	})

	// Question Managing
	g_Helper.hookElementEvent(btn_add_question, "click", true, createQuestion)

	g_Helper.hookElementEvent(btn_delete_question, "click", true, deleteQuestion)

	// All done
	g_Helper.hookElementEvent(btn_submit_assignment, "click", true, () =>
	{
		const assignment_form_data = document.querySelector("#assignment_form_data")
		assignment_form_data.value = JSON.stringify(js_to_sql(g_Assignment))
	})

	// Yay
	g_Helper.hookEvent(window, "resetup_current_question", true, () =>
	{
		goToQuestion(g_CurrentQuestionNumber)
	})
})
