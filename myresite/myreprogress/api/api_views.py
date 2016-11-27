import json

from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect, csrf_exempt, ensure_csrf_cookie
from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.http import JsonResponse, Http404, HttpResponseNotFound, HttpResponseServerError
from ..models import Book, BookPage, PageInsertionError
from .data_constructor import construct_pages

SUCCESS_JSON_DICT = {"status": "OK"}
SUCCESS_RESPONSE = JsonResponse(SUCCESS_JSON_DICT)

def getPostData(request):
	return json.loads(request.body.decode())

def apiBookPages(request, book_id):
	book = Book.objects.get(pk=book_id)
	book_name = book.book_name
	book_pages = BookPage.objects.filter(book=book_id)

	return JsonResponse(construct_pages(book_name, book_pages))


@ensure_csrf_cookie
@require_http_methods(["POST"])
@user_passes_test(lambda user: user.is_staff)
def apiTogglePageProperty(request, book_id, page_id):
	try:
		page = BookPage.objects.get(book=book_id, page_number=page_id)
	except :
		raise Http404("Page does not exist!")

	data = getPostData(request)
	prperty = data["property"]

	try:
		setattr(page, prperty, not getattr(page, prperty))  # toggling
		new_prperty = getattr(page, prperty)
	except AttributeError:
		return HttpResponseNotFound("Property does not exist!")

	page.save()  # saving is needed!

	response = {'value': int(new_prperty), 'property': prperty}
	response.update(SUCCESS_JSON_DICT)

	return JsonResponse(response)

@csrf_exempt # todo: set CSRF protection after testing
# @ensure_csrf_cookie
@require_http_methods(["POST"])
# @user_passes_test(lambda user: user.is_staff) # todo: uncomment after testing!
def apiInsertPages(request, book_id):
	data = getPostData(request)
	# a position where the pages will be inserted, basically the page BEFORE which the new pages are put.
	insert_at = int(data["insert_at"])# todo: handle exceptions for unfound attributes in getPostData!
	# amount of pages to insert
	pages_amount = int(data["pages_amount"])

	try:
		BookPage.objects.insertPages(book_id, insert_at, pages_amount)
	except PageInsertionError as e:
		return HttpResponseNotFound(str(e))

	return SUCCESS_RESPONSE

@csrf_exempt # todo: set CSRF protection after testing
# @ensure_csrf_cookie
@require_http_methods(["POST"])
# @user_passes_test(lambda user: user.is_staff) # todo: uncomment after testing!
def apiValidatePages(request, book_id):
	# data = getPostData(request)
	# a position where the pages will be inserted, basically the page BEFORE which the new pages are put.
	# insert_at = int(data["insert_at"])# todo: handle exceptions for unfound attributes in getPostData!
	# amount of pages to insert
	# pages_amount = int(data["pages_amount"])

	try:
		BookPage.objects.validatePageNumbers(book_id)
	except Exception as e:
		return HttpResponseServerError(str(e))

	return SUCCESS_RESPONSE