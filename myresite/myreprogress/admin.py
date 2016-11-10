from django.contrib import admin
from .models import BookPage, Book


class BookPageAdmin(admin.ModelAdmin):
	pass
	# fields = ('page_number',)

class BookAdmin(admin.ModelAdmin):
	pass

admin.site.register(BookPage, BookPageAdmin)
admin.site.register(Book, BookAdmin)
