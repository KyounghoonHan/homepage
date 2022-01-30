from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post

# Create your tests here.


class TestView(TestCase):
    def setUp(self):
        self.client = Client()

    def navbar_test(self, soup):
        """Testing from a function call"""
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About me', navbar.text)
        
        logo_btn = navbar.find('a', text="Navigation")
        self.assertEqual(logo_btn.attrs['href'], '/')
        
        home_btn = navbar.find('a', text="Home")
        self.assertEqual(home_btn.attrs['href'], '/')
        
        blog_btn = navbar.find('a', text="Blog")
        self.assertEqual(blog_btn.attrs['href'], '/blog/')
        
        about_me_btn = navbar.find('a', text="About me")
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')

    def test_post_list(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')

        # 1. Blog title has 'Blog'
        self.assertIn('Blog', soup.title.text)

        # 2. 'Blog and About me' are included in Navbar
        self.navbar_test(soup)
        
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

    def test_post_detail(self):

        # 1. One post exists
        post_001 = Post.objects.create(
            title="First post",
            content="Hello"
        )

        self.assertTrue(Post.objects.count(), 1)

        # 2. The post url is '/blog/1/'
        self.assertEqual(post_001.get_absolute_url(), '/blog/1/')

        # 3. Return 200 response
        response = self.client.get('/blog/1/')
        self.assertEqual(response.status_code, 200)

        # 4. 'Blog' exists in Navbar
        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)

        # 5. Main area has a post title
        main_area = soup.find('div', id='main-area')
        self.assertIn('First post', main_area.text)
