from unicodedata import category
from django.shortcuts import render
from .models import Post, Category

from django.views.generic import ListView, DetailView
# Create your views here.


class PostList(ListView):
    model = Post
    template_name = 'blog/index.html' # set a template manually
    ordering = '-pk'
    
    def get_context_data(self, **kwargs):
        """Pass non-default data"""
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        
        return context
    
class PostDetail(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        """Pass non-default data"""
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        
        return context


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