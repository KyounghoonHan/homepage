from django.shortcuts import render
from .models import Post

# Create your views here.
def index(request):
    posts = Post.objects.all().order_by('-pk')
    context = {'posts': posts}
    
    return render(
        request,
        'blog/index.html',
        context
    )
    
def single_page_post(request, pk):
    post = Post.objects.get(pk=pk)
    context = {'post': post}
    
    return render(
        request,
        'blog/single_page.html',
        context
    )