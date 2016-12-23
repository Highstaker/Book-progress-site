from django.core.validators import MinValueValidator
from django.db import models
from django_extensions.db.fields import AutoSlugField
from django.db import transaction


class PageMovementError(Exception):
	pass


class PageInsertionError(Exception):
	pass


class ArgumentError(Exception):
	pass

def get_book(func):
	def wrapper(*args, **kwargs):
		try:
			book = kwargs['book']
			if isinstance(book, int):
				kwargs['book'] = Book.objects.get(pk=book)
		except KeyError:
			# print(func.__name__, "get_book called but no book keyword provided!")
			book = args[0]
			if isinstance(book, int):
				args = (Book.objects.get(pk=book),) + args[1:]
		result = func(*args,**kwargs)
		return result
	return wrapper

class PageQuerySet(models.query.QuerySet):
	def movePagesBy(self, starting, steps):
		"""
		Moves all pages from `starting` and onward by `steps` steps.
		:param starting: page number! not the index! They start at one and end at `len`.
		Inclusive (page `stating` is the first one to be moved)
		:param steps:
		:return:
		"""
		sliced = self.filter(page_number__gte=starting)

		if steps < 0:
			# check for collisions or going into <=0
			real_starting = sliced.aggregate(real_starting=models.Min('page_number'))["real_starting"]
			if real_starting + steps <= 0:
				raise PageMovementError("Some page numbers will result at 0 or negative. This is not permitted!")
			elif len(self.filter(page_number__lt=real_starting, page_number__gte=real_starting+steps)):
				# there are pages in the way!
				raise PageMovementError("Cannot move! There are existing pages in the way.")

		# moves all pages by `steps`.
		sliced.update(page_number=models.F('page_number')+steps)

	def validatePageNumbers(self):
		"""
		Moves all pages so their page numbers would be consecutive.
		:return:
		"""
		with transaction.atomic():
			prev_page = 0
			for page in self:
				if page.page_number > prev_page+1:
					# print("validatePageNumbers", "prev_page", prev_page, "cur_page", page.page_number)#debug
					page.page_number = prev_page+1
					page.save()
				prev_page = page.page_number


class BookPageManager(models.Manager):
	def get_queryset(self):
		return PageQuerySet(self.model, using=self._db)

	@get_book
	def create(self, *args, **kwargs):
		super(BookPageManager, self).create(*args, **kwargs)

	@get_book
	def getSortedPagesQueryset(self, book):
		"""
		Returns a QuerySet of pages from given book sorted by page number.
		:param book: an integer
		:return:
		"""
		return self.filter(book=book).order_by('page_number')


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
	book_slug = AutoSlugField(max_length=300, unique=True, blank=False, populate_from=('book_name',))

	def __str__(self):
		return "{}".format(self.book_name)

	def __repr__(self):
		return "Book {}".format(self.pk)

	# TODO: create getPages() method to get all pages of a book from book model

	def getPages(self):
		"""
		Calls BookPage.objects.getSortedPagesQueryset to return a sorted QuerySet of all pages in this book
		:return: sorted QuerySet of all pages in this book
		"""
		return BookPage.objects.getSortedPagesQueryset(self)

	def insertPages(self, at, amount):
		"""

		:param book: an integer
		:param at: pages are inserted BEFORE this page. If at is >= total pages, inserts at the end
		:param amount:
		:return:
		"""
		if at < 1:
			raise PageInsertionError("starting index too low!")
		if amount < 1:
			raise PageInsertionError("cannot insert 0 or negative number of pages!")

		pages = BookPage.objects.getSortedPagesQueryset(self)
		if at > len(pages):
			# `at` is beyond the end. Set it to the end.
			at = len(pages) + 1
		else:
			pages.movePagesBy(at, amount)

		with transaction.atomic():
			for page_num in range(at, at + amount):
				BookPage.objects.create(page_number=page_num, book=self)

		return True

	def validatePageNumbers(self):
		pages = BookPage.objects.getSortedPagesQueryset(self)
		pages.validatePageNumbers()
		return True

	def deletePages(self, page_numbers_to_delete):
		"""

		:param book:
		:param page_numbers_to_delete: list of pages to delete, or one integer to delete one page
		:raises:ArgumentError - when `page_numbers_to_delete` is neither an integer nor an iterable
		:return: number of pages deleted
		"""
		pages = BookPage.objects.getSortedPagesQueryset(self)
		if isinstance(page_numbers_to_delete, int):
			# one page provided as integer
			page_numbers_to_delete = (page_numbers_to_delete,)

		try:
			pages_to_delete = pages.filter(page_number__in=page_numbers_to_delete)
		except TypeError as e:
			raise ArgumentError("The page number argument is neither an integer nor an iterable!")

		deletion_result = pages_to_delete.delete()
		number_of_pages_deleted = deletion_result[0]
		pages.validatePageNumbers()

		return number_of_pages_deleted

	# objects = BookManager()  # the manager for book pages
