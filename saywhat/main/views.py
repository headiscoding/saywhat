from django.shortcuts import render, get_object_or_404
from .forms import PostModelForm, CommentModelForm
from time import asctime
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from .models import Post, Comment
from django.views.generic import ListView, DeleteView, UpdateView
from django.contrib.auth.decorators import login_required



class ListPostView(ListView):
    model = Post
    template_name = 'index.html'

def index_view(req):
    posts = Post.objects.order_by('-id')
    return render(req, 'index.html', {'object_list': posts, 'page': 'main'})

def index_view_hot(req):
    posts = list(Post.objects.all())
    posts.sort(key=lambda x: x.get_total_likes(), reverse=True)
    return render(req, 'index.html', {'object_list': posts, 'page': 'hot'})
    
def new_post(req):
    if req.user.is_authenticated:
        if req.method == 'POST':
            form = PostModelForm(req.POST or None)
            instance = form.save(commit=False)
            instance.op = req.user
            instance.save()
            return HttpResponseRedirect('/')
        else:
            form = PostModelForm(instance=req.user)
            return render(req, 'newpost.html', {'form': form})
    else:
        return HttpResponseRedirect('/')
def view_post(req, key):
    post = Post.objects.get(pk=key)
    total_likes = post.get_total_likes()
    liked = False
    canEdit = True if req.user == post.op else False
    canDelete = canEdit
    if post.upvotes.filter(id=req.user.id).exists():
        liked =True
    return render(req,'post.html', {'post': post, 'total_likes': total_likes, 'liked': liked, 'canDelete': canDelete, 'canEdit': canEdit})

def like_post(req, pk):
    post = get_object_or_404(Post, id=req.POST.get('post_id'))
    liked = False
    if post.upvotes.filter(id=req.user.id).exists():
        post.upvotes.remove(req.user)
        liked = False
    else:
        liked = True
        post.upvotes.add(req.user)
    post.save()
    return HttpResponseRedirect(f'/post/{pk}')

def new_comment(req, pk):
    try:
        post = get_object_or_404(Post, id=req.POST.get('post_id'))
        form = CommentModelForm(req.POST or None)
        instance = form.save(commit=False)
        instance.user = req.user
        instance.post = post
        instance.save()
        return HttpResponseRedirect(f'/post/{pk}')
    except Exception as e:
        print(e)
        return HttpResponseRedirect(f'/post/{pk}')
    
class DeletePost(DeleteView):
    model = Post
    success_url = '/'
    template_name = 'delete.html'
    
class EditPost(UpdateView):
    model = Post
    fields = ['title', 'body']
    template_name = 'update.html'