from django.test import TestCase
from .models import BookPage, Book, PageInsertionError, ArgumentError, PageMovementError
from django.db.utils import IntegrityError
from django.db import transaction

from time import sleep

class BookModelTestCase(TestCase):
	def test_book_creation(self):
		book = Book.objects.create(book_name="Myre 1")
		# book = Book.objects.get(pk=1)
		self.assertEqual(book.book_name, "Myre 1")
		self.assertEqual(str(book), "Myre 1")
		self.assertEqual(book.book_slug, "myre-1")

		sleep(10)

		# test creation of a book with existing name
		with transaction.atomic():
			# this is needed because each test is wrapped in a transaction,
			# so if an exception occurs, it breaks the transaction until you explicitly roll it back.
			# Therefore, any further ORM operations in that transaction
			# will fail with django.db.transaction.TransactionManagementError exception.
			self.assertRaises(IntegrityError, Book.objects.create, book_name="Myre 1")

		# test when the name is different but slug is probably the same.
		# it is not, the field will create a different one. Probably...
		book = Book.objects.create(book_name="Myre_1")
		book = Book.objects.create(book_name="Myre-1")
		print("test_book_creation books", [{"__str__": str(i),"slug": i.book_slug} for i in Book.objects.all()])

	def test_book_page_assignment(self):
		book = Book.objects.create(book_name="Myre 1")
		for i in range(1,11):
			BookPage.objects.create(book=book, page_number=i, page_name="Pagina {}".format(i))

		pages = BookPage.objects.all().order_by("page_number")
		print("test_book_page_assignment", "pages", pages)
		self.assertEqual(len(pages),10)
		for n, i in enumerate(pages):
			self.assertEqual(i.page_number, n+1)

	def test_book_deletion(self):
		# test the automatic deletion of associated pages
		book = Book.objects.create(book_name="Myre 1")
		for i in range(1,11):
			BookPage.objects.create(book=book, page_number=i, page_name="Pagina {}".format(i))

		book.delete()
		pages = BookPage.objects.all()
		print("test_book_deletion", "pages after deletion", pages)
		self.assertEqual(len(pages),0)

class PageQuerySetTestCase(TestCase):
	def setUp(self):
		Book.objects.create(book_name="Myre 1")
		Book.objects.create(book_name="Haunter of Dreams")

	def test_move_pages(self):
		# todo: complete it
		book = Book.objects.get(book_name="Myre 1")

		for i in range(1,11):
			BookPage.objects.create(book=book, page_number=i, page_name="Pagina {}".format(i))
		pages = BookPage.objects.all()

		# move forward
		pages.movePagesBy(starting=1, steps=5)
		pages = BookPage.objects.all()
		self.assertEqual(set(i.page_number for i in pages), set(range(6,16)))

		# move back
		pages.movePagesBy(starting=1, steps=-5)
		pages = BookPage.objects.all()		
		self.assertEqual(set(i.page_number for i in pages), set(range(1,11)))

		#try moving into <=0. Should raise error.
		with transaction.atomic():
			self.assertRaises(PageMovementError, pages.movePagesBy(starting=1, steps=-10))
		pages = BookPage.objects.all()		
		print(pages)#debug


		#test collision. if moving to an already existing number, should raise error


class BookPageModelTestCase(TestCase):
	def setUp(self):
		Book.objects.create(book_name="Myre 1")
		Book.objects.create(book_name="Haunter of Dreams")

	def test_page_creation(self):
		# even though I test it, book pages are not meant to be created via create(), 
		# because there is no automatic page number check. Use insertPages() instead!
		book = Book.objects.get(book_name="Myre 1")
		for i in range(1,11):
			BookPage.objects.create(book=book, page_number=i, page_name="Pagina {}".format(i))

		with transaction.atomic():
			# try creating a page without a book, should raise error
			self.assertRaises(IntegrityError, BookPage.objects.create, page_number=100, page_name="Pagina surreal")
		pages = BookPage.objects.all()
		# print("test_page_creation", "pages", pages)#debug

	def test_page_insertion(self):
		book = Book.objects.get(book_name="Myre 1")
		for i in range(1,11):
			BookPage.objects.create(book=book, page_number=i, page_name="Pagina {}".format(i))

		#10 pages created

		#try adding two more to the end
		book.insertPages(at=11, amount=2)

		#try adding three more to the end, `at` is way beyond the boundaries
		book.insertPages(at=100, amount=3)

		# check page numbers
		pages = BookPage.objects.getSortedPagesQueryset(book=book)
		self.assertEqual(set(i.page_number for i in pages), set(range(1,16)))

		#try adding 3 pages in front
		book.insertPages(at=1, amount=3)
		pages = BookPage.objects.getSortedPagesQueryset(book=book)
		for i in range(3, 13):
			self.assertEqual(pages[i].page_name, "Pagina {}".format(i-2))

		# try at and amount below 1
		with transaction.atomic(): self.assertRaises(PageInsertionError, book.insertPages, at=-1, amount=3)
		with transaction.atomic(): self.assertRaises(PageInsertionError, book.insertPages, at=0, amount=3)
		with transaction.atomic(): self.assertRaises(PageInsertionError, book.insertPages, at=1, amount=0)
		with transaction.atomic(): self.assertRaises(PageInsertionError, book.insertPages, at=1, amount=-1)


		print("test_page_insertion pages", pages)

	def test_page_number_validation(self):
		book = Book.objects.get(book_name="Myre 1")
		for i in range(3,200,2):
			BookPage.objects.create(book=book.pk, page_number=i, page_name="Pagina {}".format(i))

		book.validatePageNumbers()
		book.validatePageNumbers()

		pages = BookPage.objects.getSortedPagesQueryset(book=book)
		pages = BookPage.objects.getSortedPagesQueryset(book=book.pk)
		# print(pages)#debug
		self.assertEqual(set(i.page_number for i in pages), set(range(1, 100)))

	def test_page_deletion(self):
		book = Book.objects.get(book_name="Myre 1")
		for i in range(1,21):
			BookPage.objects.create(book=book, page_number=i, page_name="Pagina {}".format(i))

		#check singular deletion from end
		result = book.deletePages(20)
		self.assertEqual(result,1)
		pages = BookPage.objects.getSortedPagesQueryset(book=book)
		self.assertEqual(set(i.page_number for i in pages), set(range(1, 20)))
		self.assertEqual(set(i.page_name for i in pages), set("Pagina {}".format(i) for i in range(1, 20)))

		#check singular deletion from middle
		result = book.deletePages(10)
		self.assertEqual(result,1)
		pages = BookPage.objects.getSortedPagesQueryset(book=book)
		self.assertEqual(set(i.page_number for i in pages), set(range(1, 19)))
		self.assertEqual(set(i.page_name for i in pages), set("Pagina {}".format(i) for i in range(1, 20))-{"Pagina 10"})

		#check singular deletion from the beginning
		result = book.deletePages(1)
		self.assertEqual(result,1)
		pages = BookPage.objects.getSortedPagesQueryset(book=book)
		self.assertEqual(set(i.page_number for i in pages), set(range(1, 18)))
		self.assertEqual(set(i.page_name for i in pages), set("Pagina {}".format(i) for i in range(1, 20))-{"Pagina 10", "Pagina 1"})

		# trying to delete beyond the range of pages or with an empty iterable should do nothing
		result = book.deletePages(0)
		self.assertEqual(result,0)
		result = book.deletePages(-1)
		self.assertEqual(result,0)		
		result = book.deletePages(20)
		self.assertEqual(result,0)
		result = book.deletePages([-1,0,20,100,-1000])
		self.assertEqual(result,0)
		result = book.deletePages([])
		self.assertEqual(result,0)

		# providing bad argument
		with transaction.atomic():
			self.assertRaises(ArgumentError, book.deletePages, 0.5)

		result = book.deletePages([2,4,6])
		pages = BookPage.objects.getSortedPagesQueryset(book=book)
		self.assertEqual(result,3)
		self.assertEqual(set(i.page_name for i in pages), set("Pagina {}".format(i) for i in range(1, 20))-{"Pagina 10", "Pagina 1", "Pagina 3", "Pagina 5", "Pagina 7"})

		result = book.deletePages(range(-100,100))
		pages = BookPage.objects.getSortedPagesQueryset(book=book)
		self.assertEqual(result,14)
		self.assertEqual(len(pages), 0)

		# try to delete from empty set
		result = book.deletePages(1)
		pages = BookPage.objects.getSortedPagesQueryset(book=book)
		self.assertEqual(result,0)
		self.assertEqual(len(pages), 0)
