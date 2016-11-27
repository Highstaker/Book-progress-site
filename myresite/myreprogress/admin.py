from django.contrib import admin
from django.db.models import Max
from .models import BookPage, Book


class BookPageAdmin(admin.ModelAdmin):
	# fields NOT to show in Edit Page.
	list_display = ('__str__', 'page_name', 'sketched','colored','edited','proofread',)
	list_filter = ('book',)
	readonly_fields = ('page_number',)  # valid page number is assigned via overridden save() in model

	def save_model(self, request, obj, form, change):
		if not change:
			# set the page number only on creation!
			max_page = BookPage.objects.filter(book=obj.book).aggregate(Max('page_number'))['page_number__max']
			obj.page_number = max_page + 1
		obj.save()


class BookAdmin(admin.ModelAdmin):
	prepopulated_fields = {'book_slug': ('book_name',)}
	list_display = ('book_name', 'book_slug',)
	pass

admin.site.register(BookPage, BookPageAdmin)
admin.site.register(Book, BookAdmin)
