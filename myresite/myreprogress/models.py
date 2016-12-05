from django.core.validators import MinValueValidator
from django.db import models


class PageInsertionError(Exception):
	pass

class ArgumentError(Exception):
	pass


class PageQuerySet(models.query.QuerySet):
	def movePagesBy(self, starting, steps):
		"""
		Moves all pages from `starting` and onward by `steps` steps.
		:param starting: page number! not the index! They start at one and end at `len`.
		Inclusive (page `stating` is the first one to be moved)
		:param steps:
		:return:
		"""
		sliced = self.filter(page_number__gte=starting).reverse()
		# moves all pages by `steps`.
		sliced.update(page_number=models.F('page_number')+steps)
		# for page in reversed(self[starting-1:length]):
		# 	print("moving ", page.page_number)
		# 	page.page_number += steps
		# 	page.save()

	def validatePageNumbers(self):
		"""

		:return:
		"""
		#todo: make it faster. Calling save() every time is slow. Maybe F() objects? https://docs.djangoproject.com/en/1.8/topics/db/queries/#filters-can-reference-fields-on-the-model
		prev_page = 0
		for page in self:
			if page.page_number > prev_page+1:
				print("validatePageNumbers", "prev_page", prev_page, "cur_page", page.page_number)#debug
				page.page_number = prev_page+1
				page.save()
			prev_page = page.page_number

class BookPageManager(models.Manager):
	def get_queryset(self):
		return PageQuerySet(self.model, using=self._db)

	def getSortedPagesQueryset(self, book_id):
		"""
		Returns a QuerySet of pages from given book sorted by page number.
		:param book_id: an integer
		:return:
		"""
		return self.filter(book=book_id).order_by('page_number')

	def createWithBookID(self, book_id, page_number):
		"""
		Creates a page in a book with given ID
		:param book_id: an integer
		:param page_number: of the new page
		:return:
		"""
		book = Book.objects.get(pk=book_id)
		self.create(page_number=page_number, book=book)

	def insertPages(self, book_id, at, amount):
		"""

		:param book_id: an integer
		:param at: pages are inserted BEFORE this page. If at is >= total pages, inserts at the end
		:param amount:
		:return:
		"""
		if at < 1:
			raise PageInsertionError("starting index too low!")
		if amount < 1:
			raise PageInsertionError("cannot insert 0 or negative number of pages!")

		pages = self.getSortedPagesQueryset(book_id)
		if at > len(pages):
			# `at` is beyond the end. Set it to the end.
			at = len(pages)+1
		else:
			pages.movePagesBy(at, amount)

		for page_num in range(at, at+amount):
			self.createWithBookID(page_number=page_num, book_id=book_id)

		return True

	def validatePageNumbers(self, book_id):
		pages = self.getSortedPagesQueryset(book_id)
		pages.validatePageNumbers()
		return True

	def deletePages(self, book_id, page_numbers_to_delete):
		"""

		:param book_id:
		:param pages_to_delete: list of pages to delete, or one integer to delete one page
		:raises:ArgumentError - when `page_numbers_to_delete` is neither an integer nor an iterable
		:return: number of pages deleted
		"""
		pages = self.getSortedPagesQueryset(book_id)
		if isinstance(page_numbers_to_delete, int):
			# one page provided as integer
			pages_to_delete = pages.get(page_number=page_numbers_to_delete)
		else:
			try:
				pages_to_delete = pages.filter(page_number__in=page_numbers_to_delete)
			except Exception as e:
				raise ArgumentError("The page number argument is neither an integer nor an iterable!")

		deletion_result = pages_to_delete.delete()
		number_of_pages_deleted = deletion_result[0]
		pages.validatePageNumbers()
		print("deletion_result",deletion_result)#debug

		return number_of_pages_deleted






class BookPage(models.Model):

	page_number = models.IntegerField(default=1, validators=[MinValueValidator(1)],
									verbose_name="Page Number (is assigned automatically)")
	page_name = models.CharField(max_length=200, blank=True)
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
		# unique_together = (('page_number', 'book'),) # impedes movement of pages
		ordering = ('-book', '-page_number',)

	objects = BookPageManager()  # the manager for book pages


class Book(models.Model):
	book_name = models.CharField(max_length=300, unique=True)
	book_slug = models.SlugField(max_length=300, unique=True)

	def __str__(self):
		return "{}".format(self.book_name)
