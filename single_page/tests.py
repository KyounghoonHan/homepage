from django.test import TestCase, Client
from django.contrib.auth.models import User
from blog.models import Post
from bs4 import BeautifulSoup

# Create your tests here.

class TestVeiw(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_trump = User.objects.create_user(
            username='trump',
            password='somepassword'
        )
        
    def test_landing(self):
        for i in range(1, 5):
            globals()['post_00{}'.format(i)] = Post.objects.create(
                title=f'{i} post',
                content=f'{i} post',
                author=self.user_trump
            )

        response = self.client.get('')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        body = soup.body
        self.assertNotIn(post_001.title, body.text)
        self.assertIn(post_002.title, body.text)
        self.assertIn(post_003.title, body.text)
        self.assertIn(post_004.title, body.text)
        