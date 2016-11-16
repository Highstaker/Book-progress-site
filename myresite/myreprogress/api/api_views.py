import json

from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect, csrf_exempt, ensure_csrf_cookie
from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.http import JsonResponse, Http404
from ..models import Book, BookPage
from .data_constructor import construct_pages

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

	data = json.loads(request.body.decode())
	prperty = data["property"]

	try:
		setattr(page, prperty, not getattr(page, prperty))  # toggling
	except AttributeError:
		raise Http404("Property does not exist!")

	page.save()  # saving is needed!

	return JsonResponse({"status": "OK"})


# @user_passes_test()
# def apiAddPage(request):
