from django.test import TestCase
from django.urls import reverse
from .models import Book, BookPage


class ViewsTestCase(TestCase):
	def test_index(self):
		response = self.client.get(reverse('myreprogress:index'))
		self.assertEqual(response.status_code, 302)

	def test_book_selection(self):
		book1 = Book.objects.create(book_name="Myre 1")
		book2 = Book.objects.create(book_name="Haunter of Dreams")

		response = self.client.get(reverse('myreprogress:Book selection'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Myre 1")
		self.assertContains(response, "Haunter of Dreams")
		self.assertEqual(len(response.context['books']), 2)

	#todo: test book_stats