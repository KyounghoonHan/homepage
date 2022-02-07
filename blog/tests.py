from unicodedata import category
from django.test import TestCase, Client
from django.contrib.auth.models import User
from bs4 import BeautifulSoup
from pip import main
from .models import Post, Category, Tag, Comment

from time import sleep

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
        self.user_obama.is_staff = True
        self.user_obama.save()
        
        self.category_programming = Category.objects.create(
            name='programming',
            slug='programming'
        )
        
        self.category_music = Category.objects.create(
            name='music',
            slug='music'
        )
        self.tag_python_kor = Tag.objects.create(
            name='파이썬 공부',
            slug="파이선-공부"
        )
        
        self.tag_python = Tag.objects.create(
            name='python',
            slug='python'
        )
        
        self.tag_hello = Tag.objects.create(
            name='hello',
            slug='hello'
        )
                
        # 4. If 2 posts exist
        self.post_001 = Post.objects.create(
            title='First post',
            content="Hello world",
            author=self.user_trump,
            category=self.category_programming
        )
        self.post_001.tags.add(self.tag_hello)

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
        self.post_003.tags.add(self.tag_python)
        self.post_003.tags.add(self.tag_python_kor)
        
        self.comment_001 = Comment.objects.create(
            post=self.post_001,
            author=self.user_obama,
            content='First comment'
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
        self.assertIn(self.tag_hello.name, post_001_card.text)
        self.assertNotIn(self.tag_python.name, post_001_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_001_card.text)
        
        
        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)       
        self.assertNotIn(self.tag_hello.name, post_002_card.text)
        self.assertNotIn(self.tag_python.name, post_002_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_002_card.text)
        
        post_003_card = main_area.find('div', id='post-3')       
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn('No category', post_003_card.text)        
        self.assertNotIn(self.tag_hello.name, post_003_card.text)
        self.assertIn(self.tag_python.name, post_003_card.text)
        self.assertIn(self.tag_python_kor.name, post_003_card.text)
        
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
        self.assertIn(self.tag_hello.name, post_area.text)
        
        # 6. Author is placed in main area
        self.assertIn(self.user_trump.username.upper(), post_area.text)
        
        # 7. Check comments
        comment_area = soup.find('div', id='comment-area')
        comment_001_area = comment_area.find('div', id='comment-1')
        self.assertIn(self.comment_001.author.username, comment_001_area.text)
        self.assertIn(self.comment_001.content, comment_001_area.text)
        
    def test_comment_form(self):
        self.assertEqual(self.post_001.comment_set.count(), 1)
        
        # Without login
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        comment_area = soup.find('div', id='comment-area')
        self.assertIn('Log in and leave a comment!', comment_area.text)
        self.assertFalse(comment_area.find('form', id='comment-form'))
        
        # Logged in case
        self.client.login(username='obama', password='somepassword')
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        comment_area = soup.find('div', id='comment-area')
        self.assertNotIn('Log in and leave a comment!', comment_area.text)

        comment_form = comment_area.find('form', id='comment-form')
        self.assertTrue(comment_form.find('textarea', id='id_content'))
        response = self.client.post(
            self.post_001.get_absolute_url() + 'new_comment/',
            {
                'content': "obama's comment",
            },
            follow=True
        )
        
        self.assertTrue(response.status_code, 200)
        
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(self.post_001.comment_set.count(), 2)
        
        new_comment = Comment.objects.last()
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertIn(new_comment.post.title, soup.title.text)
        
        comment_area = soup.find('div', id='comment-area')
        new_comment_div = comment_area.find('div', id=f'comment-{ new_comment.pk }')
        self.assertIn('obama', new_comment_div.text)
        self.assertIn("obama's comment", new_comment_div.text)
        
    def test_comment_update(self):
        comment_by_trump = Comment.objects.create(
            post=self.post_001,
            author=self.user_trump,
            content="trump's comment"
        )
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # without login
        comment_area = soup.find('div', id='comment-area')
        self.assertFalse(comment_area.find('a', id='comment-1-update-btn'))
        self.assertFalse(comment_area.find('a', id='comment-2-update-btn'))
        self.assertFalse(comment_area.find('a', id=f'comment-{self.comment_001.pk}-update-btn'))
        self.assertFalse(comment_area.find('a', id=f'comment-{comment_by_trump.pk}-update-btn'))
        
        # check post page when obama logged in
        self.client.login(username='obama', password='somepassword')
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        comment_area = soup.find('div', id='comment-area')
        self.assertTrue(comment_area.find('a', id='comment-1-update-btn'))
        self.assertFalse(comment_area.find('a', id='comment-2-update-btn'))
        
        comment_001_update_btn = comment_area.find('a', id='comment-1-update-btn')
        self.assertIn('edit', comment_001_update_btn.text)
        self.assertEqual(comment_001_update_btn.attrs['href'], '/blog/update_comment/1/')
        
        # check comment update page when a user clicks edit-btn
        response = self.client.get('/blog/update_comment/1/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        self.assertEqual('Edit Comment - Blog', soup.title.text)
        update_comment_form = soup.find('form', id='comment-form')
        content_textarea = update_comment_form.find('textarea', id='id_content')
        self.assertIn(self.comment_001.content, content_textarea.text)
        
        sleep(2)
        
        response = self.client.post(
            '/blog/update_comment/1/',
            {
                'content': 'Edited comment'
            },
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        comment_001_div = soup.find('div', id='comment-1')
        self.assertIn('Edited comment', comment_001_div.text)
        self.assertIn('Updated:', comment_001_div.text)
        
    def test_comment_delete(self):
        comment_by_trump = Comment.objects.create(
            post=self.post_001,
            author=self.user_trump,
            content="Trump's comment"
        )
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(self.post_001.comment_set.count(), 2)
        
        # Without login
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        comment_area = soup.find('div', id='comment-area')
        self.assertFalse(comment_area.find('a', id='comment-1-delete-btn'))
        self.assertFalse(comment_area.find('a', id='comment-2-delete-btn'))
        
        # Trump logged in
        self.client.login(username='trump', password='somepassword')
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertFalse(comment_area.find('a', id='comment-1-delete-btn'))
        self.assertTrue(comment_area.find('a', id='comment-2-delete-btn'))
        
        comment_002_delete_modal_btn = comment_area.find('a', id='comment-2-delete-btn')
        self.assertIn('delete', comment_002_delete_modal_btn.text)
        
        # Clicked delete btn
        self.assertEqual(
            comment_002_delete_modal_btn.attrs['data-target'],
            '#deleteCommentModal-2'
        )
        
        delete_comment_modal_002 = soup.find('div', id='deleteCommentModal-2')
        self.assertIn('Are you sure?', delete_comment_modal_002.text)
        really_delete_btn_002 = delete_comment_modal_002.find('a')
        self.assertIn('Delete', really_delete_btn_002.text)
        self.assertEqual(really_delete_btn_002.attrs['href'], '/blog/delete_comment/2/')
        
        response = self.client.get('/blog/delete_comment/2/', follow=True)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        self.assertIn(self.post_001.title, soup.title.text)
        comment_area = soup.find('div', id='comment-area')
        self.assertNotIn("Trump's comment", comment_area.text)
        self.assertEqual(self.post_001.comment_set.count(), 1)
        
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
        
    def test_tag_page(self):
        """ Check tag urls are properly working"""
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        self.navbar_test(soup)
        self.category_card_test(soup)
        
        main_area = soup.find('div', id='main-area')
        self.assertIn(self.tag_hello.name, main_area.text)
        
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)
    
    def test_create_post_without_login(self):
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)
        
    def test_create_post_with_login(self):
        self.client.login(username='trump', password='somepassword')
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200) # trump is not a staff
        
        self.client.login(username='obama', password='somepassword')
        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        main_area = soup.find('div', id='main-area')
        
        self.assertIn('Create a new post', main_area.text)
        
        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)
        
        self.client.post(
            '/blog/create_post/',
            {
                'title': 'Test post form',
                'content': "Let's try it",
                'tags_str': 'new tag; 한글, python',
            }
        )
        
        last_post = Post.objects.last()
        self.assertNotEqual(last_post.author.username, 'trump')
        self.assertEqual(last_post.author.username, 'obama')
        self.assertEqual(last_post.title, 'Test post form')
        
        self.assertEqual(last_post.tags.count(), 3)
        self.assertEqual(Tag.objects.count(), 5)
        
    def test_update_post(self):
        update_post_url = f'/blog/update_post/{self.post_003.pk}/'
        
        # Unauthenticated access (without login)
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 403)
        
        # Unauthenticated access (Not the writer)
        self.assertNotEqual(self.post_003.author, self.user_trump)
        self.client.login(username='trump', password='somepassword')
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 403)
        
        # Authenticated access
        self.assertEqual(self.post_003.author, self.user_obama)
        self.client.login(username='obama', password='somepassword')
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 200)
        
        # Check update page
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual('Edit a post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Edit a post', main_area.text)
        
        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)
        self.assertIn('파이썬 공부; python', tag_str_input.attrs['value'])
        
        # Check the result of update post
        update_respose = self.client.post(
            update_post_url,
            {
                'title': 'Updated the 3rd post',
                'content': 'We are the one',
                'category': self.category_music.pk,
                'tags_str': 'python; 한글, some tag'
            },
            follow=True # This is for following a redirect page
        )
        soup = BeautifulSoup(update_respose.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('Updated the 3rd post', main_area.text)
        self.assertIn('We are the one', main_area.text)
        self.assertIn(self.category_music.name, main_area.text)
        
        self.assertIn('python', main_area.text)
        self.assertIn('한글', main_area.text)
        self.assertIn('some tag', main_area.text)
        self.assertNotIn('파이썬 공부', main_area.text)
        

