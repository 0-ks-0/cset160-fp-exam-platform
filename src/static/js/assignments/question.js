import { Helper } from "../JSModules/helper.js"
import { Enum } from "../JSModules/enum.js"

export const QUESTION_TYPE = new Enum([ "OPEN_ENDED", "MULTIPLE_CHOICE" ])

export class Question
{
	constructor(data)
	{
		const helper = Helper.assignToObject(this)

		this.m_RawData = data

		this.m_iID = helper.getNumber(data.get("id"), false, -1)
		this.m_strText = helper.getString(data.get("text"), "INVALID QUESTION")
		this.m_iType = QUESTION_TYPE.lookupValue(helper.getString(data.get("type"), QUESTION_TYPE.translateValue(QUESTION_TYPE.MIN)))
		this.m_iPoints = helper.getNumber(data.get("points"), false, 0)

		this.m_Options = []
	}

	getID()
	{
		return this.m_iID
	}

	getText()
	{
		return this.m_strText
	}

	getType()
	{
		return this.m_iType
	}

	getPoints()
	{
		return this.m_iPoints
	}

	getOptions()
	{
		return this.m_Options
	}
}
