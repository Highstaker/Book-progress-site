from django.core.validators import MinValueValidator
from django.db import models


class PageInsertionError(Exception):
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
		print("sliced", sliced)#debug
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
				print("prev_page", prev_page, "cur_page", page.page_number)#debug
				page.page_number = prev_page+1
				page.save()
			prev_page = page.page_number

class BookPageManager(models.Manager):
	def get_queryset(self):
		return PageQuerySet(self.model, using=self._db)

	def getSortedPagesQueryset(self, book_id):
		return self.filter(book=book_id).order_by('page_number')

	def createWithBookID(self, book_id, page_number):
		book = Book.objects.get(pk=book_id)
		self.create(page_number=page_number, book=book)

	def insertPages(self, book_id, at, amount):
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


class BookPage(models.Model):

	# def getMaximumPageNumber():
	# 	page_numbers = (i.page_number for i in BookPage.objects.all())
	# 	return max(page_numbers)+1

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

	# def save_direct(self, *args, **kwargs):
	# 	"""
	# 	Access the save() directly,without all the additional fluff I added for admin.
	# 	"""
	# 	super(BookPage, self).save(*args, **kwargs)

	# it is also invoked on create!
	# def save(self, *args, **kwargs):
	# 	print("overridden save()")#debug
	# 	page_numbers = {i.page_number for i in BookPage.objects.filter(book=self.book)}
	# 	if self.page_number not in page_numbers:
	# 		self.page_number = max(page_numbers) + 1
	# 	super(BookPage, self).save(*args, **kwargs)

	def __str__(self):
		return 'Page {0} of "{1}"'.format(self.page_number, self.book.book_name)

	class Meta:
		# unique_together = (('page_number', 'book'),)
		ordering = ('-book', '-page_number',)

	objects = BookPageManager()  # the manager for book pages


class Book(models.Model):
	book_name = models.CharField(max_length=300, unique=True)
	book_slug = models.SlugField(max_length=300, unique=True)

	def __str__(self):
		return "{}".format(self.book_name)
