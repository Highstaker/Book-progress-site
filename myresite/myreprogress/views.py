from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse
from .models import Book, BookPage

# def handler404(request):
#     response = render(request, '404.html')
#     response.status_code = 404
#     return response

def index(request):
    return redirect("book/")


def book_choice(request):
    books = Book.objects.all()
    return render(request, "myreprogress/book_choice.html", {"books": books})


def book_stats(request, book_id=None, book_slug=None):
    if book_slug:
        book = get_object_or_404(Book,book_slug=book_slug)
        book_id = book.pk
    book_name = get_object_or_404(Book, pk=book_id)
    book_pages = BookPage.objects.getSortedPagesQueryset(book_id)
    return render(request, "myreprogress/book_stats.html", {"book_id": book_id, "book_name": book_name, "book_pages": book_pages})
