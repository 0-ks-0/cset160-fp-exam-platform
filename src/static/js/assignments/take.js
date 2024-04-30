import { Helper } from "../JSModules/helper.js"

import { sql_to_js, js_to_sql } from "./parser.js"
import { AssignmentRenderer } from "./renderer.js"

const g_Helper = new Helper()
const g_Renderer = new AssignmentRenderer()

var question_display = null
var g_Assignment = null
var g_CurrentQuestionNumber = 0

function goToQuestion(index)
{
	g_CurrentQuestionNumber = g_Helper.clamp(index, 0, g_Assignment.getQuestions().length - 1)

	g_Renderer.renderAssignment(g_Assignment, g_CurrentQuestionNumber, question_display)
}

g_Helper.hookEvent(window, "load", false, () =>
{
	question_display = document.querySelector("#question_display")

	g_Assignment = sql_to_js(g_AssignmentData)
	goToQuestion(g_CurrentQuestionNumber)
})
