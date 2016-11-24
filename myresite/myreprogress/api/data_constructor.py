def construct_pages(book_name, book_pages):
	result = {"book_name": book_name, "pages": {}}
	for page in book_pages:
		temp = dict()
		temp["page_name"] = page.page_name
		temp["sketched"] = "true" if page.sketched else "false"
		temp["colored"] = "true" if page.colored else "false"
		temp["edited"] = "true" if page.edited else "false"
		temp["proofread"] = "true" if page.proofread else "false"

		result["pages"][page.page_number] = temp

	return result
