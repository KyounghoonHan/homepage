from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from .models import Post, Category, Tag, Comment
from .forms import CommentForm

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
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        context['comment_form'] = CommentForm

        return context


class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    fields = ['title', 'hook_text', 'content',
              'head_image', 'file_upload', 'category']

    def test_func(self):
        """ Using UserPassesTestMixin to make staff authority"""
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        """ Using LoginRequiredMixin's form_valid to fill author field automatically"""
        current_user = self.request.user
        
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            form.instance.author = current_user
            response = super(PostCreate, self).form_valid(form)
            
            tags_str = self.request.POST.get('tags_str')
            
            if tags_str:
                tags_str = tags_str.strip()
                tags_str = tags_str.replace(',', ';')
                tags_list = tags_str.split(';')
                
                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)
            return response
        else:
            return redirect('/blog/')


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'hook_text', 'content',
            'head_image', 'file_upload', 'category']
    template_name = 'blog/post_update_form.html' # Default template is post_form
    
    def dispatch(self, request, *args, **kwargs):
        """ Dispatch is for finding out that the request is 'get' or 'post'.
            However, in this case, it is used for checking authentication """
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super(PostUpdate, self).get_context_data()
        if self.object.tags.exists():
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_default'] = '; '.join(tags_str_list)
        return context
    
    def form_valid(self, form):
        response = super(PostUpdate, self).form_valid(form)
        self.object.tags.clear()
        
        tags_str = self.request.POST.get('tags_str')
        if tags_str:
            tags_str = tags_str.strip()
            tags_str = tags_str.replace(',', ';')
            tags_list = tags_str.split(';')
            
            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(name=t)
                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)
                    tag.save()
                self.object.tags.add(tag)
        
        return response


class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(CommentUpdate, self).dispatch(request, *args, **kwargs)
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

def new_comment(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, pk=pk)
        
        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect(comment.get_absolute_url())
        else:
            redirect(post.get_absolute_url())
    else:
        raise PermissionDenied
    
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post = comment.post
    
    if request.user == comment.author:
        comment.delete()
        return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied