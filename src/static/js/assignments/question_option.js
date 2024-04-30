import { Helper } from "../JSModules/helper.js"

export class QuestionOption
{
	constructor(data)
	{
		const helper = Helper.assignToObject(this)

		this.m_RawData = data

		this.m_iID = helper.getNumber(data.get("id"), false, -1)
		this.m_strText = helper.getString(data.get("text"), "Option Text")
		this.m_bIsCorrect = helper.getBoolean(data.get("is_correct"), true)
	}

	getID()
	{
		return this.m_iID
	}

	getText()
	{
		return this.m_strText
	}

	getCorrect()
	{
		return this.m_bIsCorrect
	}
}
