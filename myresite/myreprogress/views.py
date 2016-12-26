from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse

from .models import Book, BookPage
from .forms import PageInsertForm


def index(request):
    return redirect("book/")


def book_choice(request):
    books = Book.objects.all()
    return render(request, "myreprogress/book_choice.html", {"books": books})


def book_stats(request, book_id=None, book_slug=None):
    if book_slug:
        book = get_object_or_404(Book, book_slug=book_slug)
        book_id = book.pk
    book_name = get_object_or_404(Book, pk=book_id)
    book_pages = BookPage.objects.getSortedPagesQueryset(book_id)

    # insert page form
    insert_form = None
    if request.user.is_staff:
        if request.method == 'POST':
            insert_form = PageInsertForm(request.POST)

            if insert_form.is_valid():
                pass
                # nothing happens here, everything is handled via JS and AJAX
                # print("LOL"*100)
        else:
            insert_form = PageInsertForm()
    else:
        insert_form = None

    return render(request, "myreprogress/book_stats.html", {"book_id": book_id, "book_name": book_name,
                                                            "book_pages": book_pages, "insert_page_form": insert_form})
