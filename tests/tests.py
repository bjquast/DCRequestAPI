import unittest
import pudb
from pyramid import testing
from pyramid.request import Request

'''
class ViewsTests(unittest.TestCase):
	def setUp(self):
		from dwb_authentication.security import SecurityPolicy
		self.config = testing.setUp()
		self.config.set_security_policy(SecurityPolicy())
		self.config.include('pyramid_chameleon')
		

	def tearDown(self):
		testing.tearDown()

	def test_registration(self):
		from DCRequestAPI.views.viewsIUPartsList import IUPartsListView
		request = Request.blank('/list')
		# request = testing.DummyRequest()
		response = IUPartsListView(request).IUPartsListHTML()
		self.assertEqual(response.status_code, 200)
'''


class FunctionalTests(unittest.TestCase):
	def setUp(self):
		from DCRequestAPI import main
		from webtest import TestApp
		app = main({})
		self.testapp = TestApp(app)

	def test_list(self):
		res = self.testapp.get('/list', status=200)
		self.assertIn(b'<h2>LIB collections cataloque</h2>', res.body)


if __name__ == '__main__':
	unittest.main()
