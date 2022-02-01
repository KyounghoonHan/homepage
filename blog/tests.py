from unicodedata import category
from django.test import TestCase, Client
from django.contrib.auth.models import User
from bs4 import BeautifulSoup
from pip import main
from .models import Post, Category

# Create your tests here.


class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_trump = User.objects.create_user(
            username='trump',
            password='somepassword'
        )
        self.user_obama = User.objects.create_user(
            username='obama',
            password='somepassword'
        )
        
        self.category_programming = Category.objects.create(
            name='programming',
            slug='programming'
        )
        
        self.category_music = Category.objects.create(
            name='music',
            slug='music'
        )
        
        # 4. If 2 posts exist
        self.post_001 = Post.objects.create(
            title='First post',
            content="Hello world",
            author=self.user_trump,
            category=self.category_programming
        )

        self.post_002 = Post.objects.create(
            title='Second post',
            content="Hello world",
            author=self.user_obama,
            category=self.category_music
        )
        
        self.post_003 = Post.objects.create(
            title='Third post',
            content="Hello",
            author=self.user_obama,
        )
        
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

    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        
        self.assertIn(
            f'{self.category_programming} ({self.category_programming.post_set.count()})',
            categories_card.text
        )
        self.assertIn(
            f'{self.category_music} ({self.category_music.post_set.count()})',
            categories_card.text
        )
        self.assertIn(
            f'No category ({Post.objects.filter(category=None).count()})',
            categories_card.text
        )

    def test_post_list_with_post(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')

        # 1. Blog title has 'Blog'
        self.assertIn('Blog', soup.title.text)

        # 2. 'Blog and About me' are included in Navbar
        self.navbar_test(soup)
        
        # 3. Check category is working well
        self.category_card_test(soup)
       
        # 4. Check 3 posts exist
        self.assertEqual(Post.objects.count(), 3)

        main_area = soup.find('div', id='main-area')
        self.assertNotIn('No posts', main_area.text)

        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        
        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)       
        
        post_003_card = main_area.find('div', id='post-3')       
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn('No category', post_003_card.text)        
        
        self.assertIn(self.post_001.author.username.upper(), main_area.text)
        self.assertIn(self.post_002.author.username.upper(), main_area.text)

    def test_post_list_without_post(self):
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        
        # 3. If no posts
        res = self.client.get('/blog/')
        self.assertEqual(res.status_code, 200)        

        soup = BeautifulSoup(res.content, 'html.parser')
        self.navbar_test(soup)        

        main_area = soup.find('div', id='main-area')
        self.assertIn('No posts', main_area.text)        

    def test_post_detail(self):

        self.assertTrue(Post.objects.count(), 3)

        # 2. The post url is '/blog/1/'
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')

        # 3. Return 200 response
        response = self.client.get('/blog/1/')
        self.assertEqual(response.status_code, 200)

        # 4. 'Blog' exists in Navbar
        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        
        # 3. Check category is working well
        self.category_card_test(soup)

        # 5. Check Post area
        post_area = soup.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.post_001.category.name, post_area.text)
        
        # 6. Author is placed in main area
        self.assertIn(self.user_trump.username.upper(), post_area.text)
        
    def test_category_page(self):
        """Check category urls are working"""
        response = self.client.get(self.category_programming.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)
        
        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_programming.name, main_area.h1.text)
        self.assertIn(self.category_programming.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)
        
        
        
        