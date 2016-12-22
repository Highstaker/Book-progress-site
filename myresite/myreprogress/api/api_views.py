import json
from functools import wraps

from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect, csrf_exempt, ensure_csrf_cookie
from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.http import JsonResponse, Http404, HttpResponseNotFound, HttpResponseServerError, HttpResponseForbidden, HttpResponseBadRequest
from ..models import Book, BookPage, PageInsertionError
from .data_constructor import construct_pages

SUCCESS_JSON_DICT = {"status": "OK"}
SUCCESS_RESPONSE = JsonResponse(SUCCESS_JSON_DICT)

class PostDataError(Exception):
	pass

def user_is_staff_or_forbidden(f):
	@wraps(f)
	def _wrapped_view(request, *args, **kwargs):
		if not request.user.is_staff:
			return HttpResponseForbidden("Not staff!")
		else:
			return f(request, *args, **kwargs)
	return _wrapped_view

def getPostData(request):
	try:
		return json.loads(request.body.decode())
	except Exception as e:
		raise PostDataError("Could not get POST data: " + str(e))

def apiBookPages(request, book_id):
	try:
		book = Book.objects.get(pk=book_id)
	except Book.DoesNotExist:
		raise Http404("Book with id {} does not exist!".format(book_id))
	book_name = book.book_name
	book_pages = BookPage.objects.filter(book=book_id)

	return JsonResponse(construct_pages(book_name, book_pages))


@ensure_csrf_cookie
@require_http_methods(["POST"])
@user_is_staff_or_forbidden
def apiTogglePageProperty(request, book_id, page_number):
	try:
		page = BookPage.objects.get(book=book_id, page_number=page_number)
	except :
		raise Http404("Page does not exist!")

	try:
		data = getPostData(request)
	except PostDataError as e:
		return HttpResponseBadRequest(str(e))

	try:
		prperty = data["property"]
	except KeyError:
		return HttpResponseBadRequest("Data contains no properties!")

	try:
		setattr(page, prperty, not getattr(page, prperty))  # toggling
		new_prperty = getattr(page, prperty)
	except AttributeError:
		return HttpResponseNotFound("Property does not exist!")

	page.save()  # saving is needed!

	response = {'value': int(new_prperty), 'property': prperty}
	response.update(SUCCESS_JSON_DICT)

	return JsonResponse(response)

# @csrf_exempt # todo: set CSRF protection after testing
@ensure_csrf_cookie
@require_http_methods(["POST"])
@user_is_staff_or_forbidden # todo: uncomment after testing!
def apiInsertPages(request, book_id):
	try:
		book = Book.objects.get(pk=book_id)
	except :
		raise Http404("Book does not exist!")

	try:
		data = getPostData(request)
	except PostDataError as e:
		return HttpResponseBadRequest(str(e))

	try:
		# a position where the pages will be inserted, basically the page BEFORE which the new pages are put.
		insert_at = int(data["insert_at"])
		# amount of pages to insert
		pages_amount = int(data["pages_amount"])
	except ValueError:
		return HttpResponseBadRequest("Data is not numerical!")
	except KeyError:
		return HttpResponseBadRequest("Data does nto contain parameters!")

	try:
		book.insertPages(insert_at, pages_amount)
	except PageInsertionError as e:
		return HttpResponseNotFound(str(e))

	return SUCCESS_RESPONSE

# @csrf_exempt # todo: set CSRF protection after testing
@ensure_csrf_cookie
@require_http_methods(["POST"])
@user_is_staff_or_forbidden # todo: uncomment after testing!
def apiValidatePages(request, book_id):
	try:
		book = Book.objects.get(pk=book_id)
	except :
		raise Http404("Book does not exist!")

	try:
		book.validatePageNumbers()
	except Exception as e:
		return HttpResponseServerError(str(e))

	return SUCCESS_RESPONSE

# @csrf_exempt # todo: set CSRF protection after testing
@ensure_csrf_cookie
@require_http_methods(["POST"])
@user_is_staff_or_forbidden # todo: uncomment after testing!
def apiDeletePages(request, book_id):
	data = getPostData(request)
	# todo: validate all received data!

	# a list
	pages_to_delete = data["pages_to_delete"]

	number_of_pages_deleted = BookPage.objects.deletePages(book_id, pages_to_delete)
	response = {"number_of_pages_deleted":number_of_pages_deleted}
	response.update(SUCCESS_JSON_DICT)

	return JsonResponse(response)
