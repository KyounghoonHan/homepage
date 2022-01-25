from django.shortcuts import render
from .models import Post

from django.views.generic import ListView
# Create your views here.


class PostList(ListView):
    """ PostList by CBV """
    model = Post
    template_name = 'blog/index.html' # set a template manually
    ordering = '-pk'
    

# def index(request):
    """ index by FBV """
#     posts = Post.objects.all().order_by('-pk')
#     context = {'posts': posts}
    
#     return render(
#         request,
#         'blog/index.html',
#         context
#     )
    
def single_page_post(request, pk):
    post = Post.objects.get(pk=pk)
    context = {'post': post}
    
    return render(
        request,
        'blog/single_page.html',
        context
    )