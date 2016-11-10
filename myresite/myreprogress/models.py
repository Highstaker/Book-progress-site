from django.db import models


class BookPage(models.Model):
	page_number = models.IntegerField(default=0)
	# link to book object this page belongs to.
	book = models.ForeignKey('Book', on_delete=models.CASCADE)

	sketched = models.BooleanField(default=False)
	colored = models.BooleanField(default=False)
	edited = models.BooleanField(default=False)
	proofread = models.BooleanField(default=False)

	# extra_fields = models.TextField(default=)

	def __str__(self):
		return 'Page {0} of "{1}"'.format(self.page_number, self.book.book_name)

	class Meta:
		unique_together = (('page_number', 'book'),)


class Book(models.Model):
	book_name = models.CharField(max_length=300, unique=True)

	def __str__(self):
		return "{}".format(self.book_name)
