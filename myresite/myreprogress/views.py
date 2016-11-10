from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the myreprogress index.")

def book_choice(request):
    return HttpResponse("Pick a book")

def book_stats(request, book_id):
    return HttpResponse("Book {} stats".format(book_id))