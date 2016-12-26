from django.contrib import admin
from django.db.models import Max
from .models import BookPage, Book

#TODO: check and test!

class BookPageAdmin(admin.ModelAdmin):
	# fields NOT to show in Edit Page.
	list_display = ('__str__', 'page_name', 'sketched', 'colored', 'edited', 'proofread',)
	list_filter = ('book',)
	readonly_fields = ('page_number',)  # valid page number is assigned via overridden save() in model
	actions = ['delete_selected',]

	def save_model(self, request, obj, form, change):
		if not change:
			# set the page number only on creation!
			max_page = BookPage.objects.filter(book=obj.book).aggregate(Max('page_number'))['page_number__max']
			obj.page_number = max_page + 1
		obj.save()  # the parent does only this

	def delete_model(self, request, obj):
		book = obj.book
		super(BookPageAdmin, self).delete_model(request, obj)
		book.validatePageNumbers()

	def delete_selected(self, request, obj):
		# kinda overriding default 'delete_selected' action to make it perform page validation afterwards
		books = {i.book for i in obj}
		obj.delete()
		for b in books:
			# perform validation for all books the pages of which were deleted
			b.validatePageNumbers()


class BookAdmin(admin.ModelAdmin):
	list_display = ('book_name', 'book_slug',)

admin.site.register(BookPage, BookPageAdmin)
admin.site.register(Book, BookAdmin)
