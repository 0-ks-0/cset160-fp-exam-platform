import { Helper } from "../JSModules/helper.js"
import { DOMBuilder } from "../JSModules/dom_builder.js"

import { QUESTION_TYPE } from "./question.js"
import { QuestionOption } from "./question_option.js"

export class AssignmentRenderer
{
	constructor()
	{
		Helper.assignToObject(this)

		this.m_Builder = new DOMBuilder()
	}

	renderOpenEnded(question, renderTarget, editable)
	{
		const builder = this.m_Builder

		builder.start(renderTarget)
		{
			builder.startElement("textarea")
			{

			}
			builder.endElement()
		}
		builder.end()
	}

	renderMultipleChoice(question, renderTarget, editable)
	{
		const helper = this.getHelper()
		const builder = this.m_Builder

		builder.start(renderTarget)
		{
			if (editable)
				builder.startElement("div")

			const options = question.getOptions()
			for (const option of options)
			{
				const optionText = option.getText()
				const optionID = optionText + options.indexOf(option)

				var row = null

				if (editable)
				{
					row = builder.startElement("div")
					{
						builder.addClass("flexbox")

						builder.setProperty("m_Question", question)
						builder.setProperty("m_Option", option)
					}
				}

				builder.startElement("input")
				{
					builder.addClass("question_option")

					builder.setAttribute("type", "radio")
					builder.setAttribute("name", "question_option")


					if (option.getCorrect())
						builder.setAttribute("checked", true)

					builder.setProperty("id", optionID)
				}
				builder.endElement()

				if (editable)
				{
					const optionInput = builder.startElement("input")
					{
						builder.setAttribute("type", "text")
						builder.setAttribute("value", option.getText())

						const thing = (_, self) =>
						{
							self.m_Option.m_strText = self.value
						}

						helper.hookElementEvent(optionInput, "change", true, thing)
						helper.hookElementEvent(optionInput, "keypress", true, thing)
						helper.hookElementEvent(optionInput, "paste", true, thing)
						helper.hookElementEvent(optionInput, "input", true, thing)

						builder.setProperty("m_Option", option)
					}
					builder.endElement()

					const trash = builder.startElement("ion-icon")
					{
						builder.addClass("real_button")

						builder.setAttribute("name", "trash-outline")

						helper.hookElementEvent(trash, "click", true, (_, self) =>
						{
							const question = self.m_Row.m_Question

							helper.popFrom(question.getOptions(), self.m_Row.m_Option)

							self.m_Row.remove()
						})

						builder.setProperty("m_Row", row)
					}
					builder.endElement()
				}
				else
				{
					builder.startElement("label")
					{
						builder.addClass("question_option_label")

						builder.setAttribute("for", optionID)

						builder.setProperty("innerHTML", optionText)
					}
					builder.endElement()

					builder.startElement("br")
					builder.endElement()
				}

				if (editable)
					builder.endElement()
			}

			if (editable)
			{
				{
					const add = builder.startElement("ion-icon")
					{
						builder.addClass("real_button")

						builder.setAttribute("name", "add-circle-outline")

						helper.hookElementEvent(add, "click", true, (_, self) =>
						{
							question.getOptions().push(new QuestionOption(new Map()))

							window.dispatchEvent(new Event("resetup_current_question"))
						})

						builder.setProperty("m_Row", row)
						builder.setProperty("id", "add_question_option")
					}
					builder.endElement()
				}
				builder.endElement()
			}
		}
		builder.end()
	}

	renderAssignment(assignment, questionNumber, renderTarget, editable)
	{
		const helper = this.getHelper()

		if (!helper.isValidElement(renderTarget))
			return

		renderTarget.innerHTML = ""

		const question = assignment.getQuestion(questionNumber)
		if (!question)
		{
			console.error("Invalid question (?)")
			return
		}

		const builder = this.m_Builder

		// Main question
		builder.start(renderTarget)
		{
			if (editable)
			{
				const titleInput = builder.startElement("input")
				{
					builder.setAttribute("type", "text")
					builder.setAttribute("value", question.getText())

					const thing = (_, self) =>
					{
						self.m_Question.m_strText = self.value
					}

					helper.hookElementEvent(titleInput, "change", true, thing)
					helper.hookElementEvent(titleInput, "keypress", true, thing)
					helper.hookElementEvent(titleInput, "paste", true, thing)
					helper.hookElementEvent(titleInput, "input", true, thing)

					builder.setProperty("style.display", "block")
					builder.setProperty("m_Question", question)
				}
				builder.endElement()
			}
			else
			{
				builder.startElement("h3")
				{
					builder.setProperty("innerHTML", question.getText())
				}
				builder.endElement()
			}
		}
		builder.end()

		// The rest
		switch (question.getType())
		{
			default:
			case QUESTION_TYPE.OPEN_ENDED:
				this.renderOpenEnded(question, renderTarget, editable)
				break

			case QUESTION_TYPE.MULTIPLE_CHOICE:
				this.renderMultipleChoice(question, renderTarget, editable)
				break
		}
	}
}
