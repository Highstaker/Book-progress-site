import json
from django.test import TestCase
from .models import Book, BookPage
from django.urls import reverse
from django.contrib.auth.models import User


class APIViewsTestCase(TestCase):
	def setUp(self):
		self.my_admin = User.objects.create_superuser('highstaker', 'highstaker@test.com', "qwerty12345")
		self.regular_user = User.objects.create_user('dummy', 'dummy@dummy.dum', 'asdfghjkl12345')

	def test_toggle_page_property(self):
		PAGE_NAME = "myreprogress:API. Set page property"
		book1 = Book.objects.create(book_name="Myre 1")
		book2 = Book.objects.create(book_name="Haunter of Dreams")

		book1.insertPages(at=2, amount=10)

		# test with GET, should return status 405 because only POST is allowed
		response = self.client.get(reverse(PAGE_NAME,
										kwargs={'book_id': '1', 'page_number': '1'}))
		self.assertEqual(response.status_code, 405)

		# try posting without logging in, should raise 403
		response = self.client.post(reverse(PAGE_NAME,
										kwargs={'book_id': '1', 'page_number': '1'}))
		self.assertEqual(response.status_code, 403)

		# try posting with a non-staff user, should raise 403
		response = self.client.force_login(self.regular_user)
		response = self.client.post(reverse(PAGE_NAME,
										kwargs={'book_id': '1', 'page_number': '1'}))
		self.assertEqual(response.status_code, 403)
		self.client.logout()

		# response = self.client.login(username='highstaker', password='qwerty12345')
		response = self.client.force_login(self.my_admin)

		# Testing nonexistent book. should return 404
		response = self.client.post(reverse(PAGE_NAME,
											kwargs={'book_id': '10', 'page_number': '1'}))
		self.assertEqual(response.status_code, 404)

		# Testing nonexistent page. should return 404
		response = self.client.post(reverse(PAGE_NAME,
											kwargs={'book_id': '1', 'page_number': '100'}))
		self.assertEqual(response.status_code, 404)

		# Testing empty data. should return 400 - bad request
		response = self.client.post(reverse(PAGE_NAME,
											kwargs={'book_id': '1', 'page_number': '1'}))
		self.assertEqual(response.status_code, 400)

		# Testing corrupt data. should return 400 - bad request
		response = self.client.post(reverse(PAGE_NAME,
											kwargs={'book_id': '1', 'page_number': '1'}),
									content_type='application/json',
									data='{"prperty": "sketched"}',
									)
		self.assertEqual(response.status_code, 400)

		# Testing changing a property that does not exist. should return 404
		response = self.client.post(reverse(PAGE_NAME,
											kwargs={'book_id': '1', 'page_number': '1'}),
									content_type='application/json',
									data='{"property": "weird_property"}',
									)
		self.assertEqual(response.status_code, 404)

		############
		# Successes below
		############

		# Testing changing a property. should return 200 and modify that property
		response = self.client.post(reverse(PAGE_NAME,
											kwargs={'book_id': '1', 'page_number': '1'}),
									content_type='application/json',
									data='{"property": "sketched"}',
									)
		self.assertContains(response, text="OK", status_code=200,)
		page = BookPage.objects.get(book=book1, page_number=1)

		# self.assertEqual(page.sketched, True)
		self.assertEqual(page.colored, False)
		self.assertEqual(page.edited, False)
		self.assertEqual(page.proofread, False)

		# Testing changing a property. should return 200 and modify that property
		response = self.client.post(reverse(PAGE_NAME,
											kwargs={'book_id': '1', 'page_number': '1'}),
									content_type='application/json',
									data='{"property": "sketched"}',
									)
		self.assertContains(response, text="OK", status_code=200,)
		response = self.client.post(reverse(PAGE_NAME,
											kwargs={'book_id': '1', 'page_number': '1'}),
									content_type='application/json',
									data='{"property": "colored"}',
									)
		self.assertContains(response, text="OK", status_code=200,)
		response = self.client.post(reverse(PAGE_NAME,
											kwargs={'book_id': '1', 'page_number': '1'}),
									content_type='application/json',
									data='{"property": "edited"}',
									)
		self.assertContains(response, text="OK", status_code=200,)
		response = self.client.post(reverse(PAGE_NAME,
											kwargs={'book_id': '1', 'page_number': '1'}),
									content_type='application/json',
									data='{"property": "proofread"}',
									)
		self.assertContains(response, text="OK", status_code=200,)
		response = self.client.post(reverse(PAGE_NAME,
											kwargs={'book_id': '1', 'page_number': '2'}),
									content_type='application/json',
									data='{"property": "colored"}',
									)
		self.assertContains(response, text="OK", status_code=200,)
		response = self.client.post(reverse(PAGE_NAME,
											kwargs={'book_id': '1', 'page_number': '2'}),
									content_type='application/json',
									data='{"property": "edited"}',
									)
		self.assertContains(response, text="OK", status_code=200,)
		page = BookPage.objects.get(book=book1, page_number=1)
		page2 = BookPage.objects.get(book=book1, page_number=2)
		self.assertEqual(page.sketched, False)
		self.assertEqual(page.colored, True)
		self.assertEqual(page.edited, True)
		self.assertEqual(page.proofread, True)
		self.assertEqual(page2.sketched, False)
		self.assertEqual(page2.colored, True)
		self.assertEqual(page2.edited, True)
		self.assertEqual(page2.proofread, False)

		# testing after logout. Should return 403
		self.client.logout()
		response = self.client.post(reverse(PAGE_NAME,
											kwargs={'book_id': '1', 'page_number': '2'}),
									content_type='application/json',
									data='{"property": "colored"}',
									)
		self.assertEqual(response.status_code, 403)

	def test_api_book_pages(self):
		PAGE_NAME = "myreprogress:API. Book Pages"
		book1 = Book.objects.create(book_name="Myre 1")
		book2 = Book.objects.create(book_name="Haunter of Dreams")

		# trying a non-existing book
		response = self.client.get(reverse(PAGE_NAME,
										kwargs={'book_id': '33',}))
		self.assertEqual(response.status_code, 404)

		# should return an empty dictionary
		response = self.client.get(reverse(PAGE_NAME,
										kwargs={'book_id': '1',}))
		self.assertEqual(response.status_code, 200)
		data = json.loads(response.content.decode())
		self.assertEqual(data["pages"], dict())
		self.assertEqual(data["book_name"], "Myre 1")

		# should return 10 pages
		book1.insertPages(at=2, amount=10)
		response = self.client.get(reverse(PAGE_NAME,
										kwargs={'book_id': '1',}))
		self.assertEqual(response.status_code, 200)
		data = json.loads(response.content.decode())
		self.assertEqual({str(i) for i in range(1,10+1)}, set(data["pages"].keys()))
		self.assertEqual(data["book_name"], "Myre 1")

		# should return an empty dictionary
		response = self.client.get(reverse(PAGE_NAME,
										kwargs={'book_id': '2',}))
		self.assertEqual(response.status_code, 200)
		data = json.loads(response.content.decode())
		self.assertEqual(data["pages"], dict())
		self.assertEqual(data["book_name"], "Haunter of Dreams")
		
	def test_api_insert_pages(self):
		PAGE_NAME = "myreprogress:API. Add pages to book"
		book1 = Book.objects.create(book_name="Myre 1")
		book2 = Book.objects.create(book_name="Haunter of Dreams")

		# test with GET, should return status 405 because only POST is allowed
		response = self.client.get(reverse(PAGE_NAME,
										   kwargs={'book_id': '1'}))
		self.assertEqual(response.status_code, 405)

		# try posting without logging in, should raise 403
		response = self.client.post(reverse(PAGE_NAME,
											kwargs={'book_id': '1'}))
		self.assertEqual(response.status_code, 403)

		# try posting with a non-staff user, should raise 403
		response = self.client.force_login(self.regular_user)
		response = self.client.post(reverse(PAGE_NAME,
										kwargs={'book_id': '1'}))
		self.assertEqual(response.status_code, 403)
		self.client.logout()

		# response = self.client.login(username='highstaker', password='qwerty12345')
		response = self.client.force_login(self.my_admin)

		# Testing empty data. should return 400 - bad request
		response = self.client.post(reverse(PAGE_NAME,
											kwargs={'book_id': '1'}))
		self.assertEqual(response.status_code, 400)

		# Testing corrupt data. should return 400 - bad request
		response = self.client.post(reverse(PAGE_NAME,
											kwargs={'book_id': '1'}),
									content_type='application/json',
									data='{"prperty": "sketched"}',
									)
		self.assertEqual(response.status_code, 400)

		# Testing nonexistent book. should return 404
		response = self.client.post(reverse(PAGE_NAME,
											kwargs={'book_id': '10'}),
										content_type='application/json',
										data='{"insert_at": "1", "pages_amount": 1}',
										)
		self.assertEqual(response.status_code, 404)

		# Insertion of one page. Should return status 200 and add this page as page 1 of the first
		response = self.client.post(reverse(PAGE_NAME,
											kwargs={'book_id': '1'}),
										content_type='application/json',
										data='{"insert_at": 1, "pages_amount": 1}',
										)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, text="OK", status_code=200,)


		# testing after logout. Should return 403
		self.client.logout()
		response = self.client.post(reverse(PAGE_NAME,
											kwargs={'book_id': '1'}),#TODO: different params and data here
										content_type='application/json',
										data='{"insert_at": 1, "pages_amount": 10}',
									)
		self.assertEqual(response.status_code, 403)


	def test_api_validate_pages(self):
		# TODO: test it!
		pass

	def test_api_delete_pages(self):
		# TODO: test it!
		pass
