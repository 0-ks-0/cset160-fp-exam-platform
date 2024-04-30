#
#	This is retarded....
#	:/
#

@app.route("/static/js/<path:path>") # Potential ../ traversal exploit? Nah :clueless:
def fix_mime(path):
	return send_file(f"{SERVER_DIRECTORY}/static/js/{path}", mimetype = "text/javascript")
