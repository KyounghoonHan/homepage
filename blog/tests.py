from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post

# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        
    def test_post_list(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        
        soup  = BeautifulSoup(response.content, 'html.parser')
        
        # 1. Blog title has 'Blog'
        self.assertIn('Blog', soup.title.text)
        
        # 2. 'Blog and About me' are included in Navbar
        self.assertIn('Blog', soup.nav.text)
        self.assertIn('About me', soup.nav.text)
        
        # 3. If no posts
        self.assertEqual(Post.objects.count(), 0)
        main_area = soup.find('div', id='main-area')
        self.assertIn('No posts', main_area.text)
        
        # 4. If 2 posts exist
        post_001 = Post.objects.create(
            title='First post',
            content="Hello world"
        )
        
        post_002 = Post.objects.create(
            title='Second post',
            content="Hello world"
        )
        
        self.assertEqual(Post.objects.count(), 2)
        
        new_response = self.client.get('/blog/')
        soup = BeautifulSoup(new_response.content, 'html.parser')
        
        main_area = soup.find('div', id='main-area')
        
        self.assertIn(post_001.title, main_area.text)
        self.assertIn(post_002.title, main_area.text)
        self.assertNotIn('No posts', main_area.text)
        
        
        
        
        