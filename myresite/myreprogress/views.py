from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse
from django.views import View
from django.views.generic import ListView
# from django.views.generic.edit import FormMixin
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
        context['important_data'] = 'temmie Sez: "h0i!!11"'
        return context

# old function-based implementation for BookChoiceView
# def book_choice(request):
#     books = Book.objects.all()
#     return render(request, "myreprogress/book_choice.html", {"books": books})


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

        insert_page_form = PageInsertForm()

        context['book_id'] = book_id
        context['book_name'] = book_name
        context['book_pages'] = pages
        context['insert_page_form'] = insert_page_form

        return context

# old function-based implementation for BookStatsView
# def book_stats(request, book_id=None, book_slug=None):
#     if book_slug:
#         book = get_object_or_404(Book, book_slug=book_slug)
#         book_id = book.pk
#     book_name = get_object_or_404(Book, pk=book_id)
#     book_pages = BookPage.objects.getSortedPagesQueryset(book_id)
#
#     # insert page form
#     insert_form = None
#     if request.user.is_staff:
#         if request.method == 'POST':
#             insert_form = PageInsertForm(request.POST)
#
#             if insert_form.is_valid():
#                 pass
#                 # nothing happens here, everything is handled via JS and AJAX
#                 # print("LOL"*100)
#         else:
#             insert_form = PageInsertForm()
#     else:
#         insert_form = None
#
#     return render(request, "myreprogress/book_stats.html", {"book_id": book_id, "book_name": book_name,
#                                                             "book_pages": book_pages, "insert_page_form": insert_form})
