from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse
from django.views import View
from django.views.generic import ListView
from .forms import PageInsertForm

from .models import Book, BookPage
from .forms import PageInsertForm


def index(request):
    return redirect("book/")

class BookChoiceView(ListView):
    model = Book  # equivalent to providing context object of Book.objects.all() via `queryset`
    context_object_name = 'books'  # name used for books in template
    template_name = "myreprogress/book_choice.html"  # the default one would be "myreprogress/book_list.html"

    # in case I need additional parameters
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BookChoiceView, self).get_context_data(**kwargs)
        # context['important_data'] = 'temmie Sez: "h0i!!11"'
        return context


class BookStatsView(ListView):
    model = BookPage
    context_object_name = 'pages'
    template_name = "myreprogress/book_stats.html"  # the default one would be "myreprogress/bookpage_list.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BookStatsView, self).get_context_data(**kwargs)
        try:
            book = get_object_or_404(Book, book_slug=self.kwargs['book_slug'])
            book_id = book.pk
        except KeyError:
            book_id = self.kwargs['book_id']  # yeah, with `self`
            book = get_object_or_404(Book, pk=book_id)
        book_name = book.book_name
        pages = book.getPages()
        amount_of_pages = len(pages)

        insert_page_form = PageInsertForm(initial={"insert_at": amount_of_pages+1})

        context['book_id'] = book_id
        context['book_name'] = book_name
        context['book_pages'] = pages
        # context['book_pages_amount'] = len(pages)
        context['insert_page_form'] = insert_page_form

        return context
