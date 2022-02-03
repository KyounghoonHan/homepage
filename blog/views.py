from re import template
from unicodedata import category
from django.shortcuts import render, redirect
from .models import Post, Category, Tag

from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
# Create your views here.


class PostList(ListView):
    model = Post
    template_name = 'blog/index.html'  # set a template manually
    ordering = '-pk'

    def get_context_data(self, **kwargs):
        """Pass non-default data"""
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(
            category=None).count()

        return context


class PostDetail(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        """Available to pass non-default data"""
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(
            category=None).count()

        return context


class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    fields = ['title', 'hook_text', 'content',
              'head_image', 'file_upload', 'category']

    def test_func(self):
        """ Using UserPassesTestMixin to make staff authority"""
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        """ Using LoginRequiredMixin's form_valid to fill author automatically"""
        current_user = self.request.user
        
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            form.instance.author = current_user
            return super(PostCreate, self).form_valid(form)
        else:
            return redirect('/blog/')


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'hook_text', 'content',
            'head_image', 'file_upload', 'category']
    template_name = 'blog/post_update_form.html' # Default template is post_form
    
    def dispatch(self, request, *args, **kwargs):
        """ Dispatch is for finding out the request is 'get' or 'post'.
            However, in this case, it is used for checking authentication """
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied


def category_page(request, slug):
    """ List posts by category"""

    if slug == 'no_category':
        category = 'No category'
        post_list = Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category)

    context = {
        'post_list': post_list,
        'categories': Category.objects.all(),
        'no_category_post_count': Post.objects.filter(category=None).count(),
        'category': category
    }

    return render(
        request,
        'blog/index.html',
        context
    )

def tag_page(request, slug):
    """ List posts by a tag"""
    tag = Tag.objects.get(slug=slug)
    post_list = tag.post_set.all()

    context = {
        'post_list': post_list,
        'categories': Category.objects.all(),
        'no_category_post_count': Post.objects.filter(category=None).count(),
        'tag': tag
    }

    return render(
        request,
        'blog/index.html',
        context
    )

# def index(request):
    """ PostList(index) by FBV """
#     posts = Post.objects.all().order_by('-pk')
#     context = {'posts': posts}

#     return render(
#         request,
#         'blog/index.html',
#         context
#     )

# def single_page_post(request, pk):
    """ PostDetail(single_page_post) by FBV """


#     post = Post.objects.get(pk=pk)
#     context = {'post': post}

#     return render(
#         request,
#         'blog/single_page.html',
#         context
#     )
