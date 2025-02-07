from django.db.models.fields import BLANK_CHOICE_DASH
from django.http import request
from django.shortcuts import get_object_or_404, redirect, render
from .models import *
from django.db.models import Count
from django.utils import timezone
from .forms import BlogForm, CommentForm, YoutubeForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponse,JsonResponse
import json
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    blog = Blog.objects.order_by('?') #랜덤으로 줄 세우기
    notice=Notice.objects.all()
    popular_blog = Blog.objects.annotate(like_count=Count('like')).order_by('-like_count')[:4] #인기글 3개
    return render(request, 'home.html', {'blogs':blog,'popular_blogs':popular_blog, 'notices':notice}) 

def detail(request, blog_id):
    blog_detail = get_object_or_404(Blog, pk=blog_id)
    blog_hashtag = blog_detail.hashtag.all()
    return render(request, 'detail.html', {'blog':blog_detail, 'hashtags':blog_hashtag})

@login_required
def new(request):
    blogform = BlogForm()                           
    return render(request, 'new.html', {'form':blogform})

@login_required
def create(request):
    new_blog = Blog()
    new_blog.pub_date = timezone.now()
    new_blog.author = request.user
    new_blog.title = request.POST['title']
    new_blog.body=request.POST['body']
    new_blog.cover_image = request.FILES.get('cover_image')
    new_blog.save()
    hashtags = request.POST['hashtags']
    hashtag = hashtags.split(",")
    for tag in hashtag:
        ht = HashTag.objects.get_or_create(hashtag_name=tag)
        new_blog.hashtag.add(ht[0])
    return redirect('detail', new_blog.id) 
  

@login_required
def edit(request, blog_id):
    blog_detail = get_object_or_404(Blog, pk=blog_id)
    return render(request, 'edit.html', {'blog' : blog_detail})


@login_required
def update(request, blog_id):
    blog_update = get_object_or_404(Blog, pk=blog_id)
    blog_update.title = request.POST['title']
    blog_update.body = request.POST['body']
    blog_update.save()
    return redirect('home')


@login_required
def delete(request, blog_id):
    blog_delete = get_object_or_404(Blog, pk=blog_id)
    blog_delete.delete()
    return redirect('home')


@login_required
def addCommentToPost(request, blog_id): #댓글
    blog = get_object_or_404(Blog, pk = blog_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author_name = request.user
            comment.post = blog
            comment.save()
            return redirect('detail', blog_id)
    else:
        form = CommentForm()
    return render(request, 'add_comment_to_post.html',{'form':form})


@login_required
def edit_comment(request, comment_id, blog_id):  #댓글 수정 페이지로 이동
    comment = Comment.objects.get(id = comment_id)
    return render(request, 'edit_comment.html', {'comment' : comment})

@login_required
def update_comment(request,comment_id): #댓글 수정하기
    comment_update = Comment.objects.get(id = comment_id)
    comment_update.comment_text = request.POST['comment_text']
    comment_update.save()
    return redirect('home')

@login_required
def delete_comment(request, blog_id, comment_id): #댓글 삭제하기
    comment_delete = Comment.objects.get(id = comment_id)
    comment_delete.delete()
    return redirect('detail', blog_id)


@login_required
def create_youtube(request, blog_id): #유튜브 게시글 추가
    blog = get_object_or_404(Blog, pk = blog_id)
    if request.method == "POST":
        form = YoutubeForm(request.POST)
        if form.is_valid():
            youtube = form.save(commit=False)
            youtube.post = blog
            youtube.save()
            return redirect('detail', blog_id)
    else:
        form = YoutubeForm()
    return render(request, 'create_youtube.html',{'form':form})


@login_required
def delete_youtube(request, blog_id, youtube_id): #영상 삭제하기
    youtube_delete = Youtube.objects.get(id = youtube_id)
    youtube_delete.delete()
    return redirect('detail', blog_id)

@login_required
def edit_youtube(request, youtube_id, blog_id):  #영상 수정 페이지로 이동
    youtube_detail = Youtube.objects.get(id = youtube_id)
    return render(request, 'edit_youtube.html', {'youtube' : youtube_detail})

@login_required
def update_youtube(request,youtube_id): #영상 수정하기
    youtube_update = Youtube.objects.get(id = youtube_id)
    youtube_update.subtitle = request.POST['subtitle']
    youtube_update.body = request.POST['body']
    youtube_update.url = request.POST['url']
    youtube_update.save()
    return redirect('home')

def video_list(request):
    video_list = Blog.objects.all()
    
    search_key = request.GET.get('search_key') # 검색어 가져오기
    if search_key: # 만약 검색어가 존재하면
        video_list = video_list.filter(title__icontains=search_key) # 해당 검색어를 포함한 queryset 가져오기

    return render(request, 'video_list.html', {'video_list':video_list})


@login_required
def mypage(request):
    myblog = Blog.objects.filter(author = request.user)
    user = request.user
    liked_blog = user.likes.all()
    user_info = request.user
    return render(request, 'mypage.html',{'myblogs': myblog, 'liked_blogs':liked_blog, 'user_infos':user_info})

def likes(request): #좋아요 기능
    if request.is_ajax(): #ajax 방식일 때 아래 코드 실행
        blog_id = request.GET['blog_id'] #좋아요를 누른 게시물id (blog_id)가지고 오기
        post = Blog.objects.get(id=blog_id) 
				
        if not request.user.is_authenticated: #버튼을 누른 유저가 비로그인 유저일 때
            message = "로그인을 해주세요" #화면에 띄울 메세지 
            context = {'like_count' : post.like.count(),"message":message}
            return HttpResponse(json.dumps(context), content_type='application/json')

        user = request.user #request.user : 현재 로그인한 유저
        if post.like.filter(id = user.id).exists(): #이미 좋아요를 누른 유저일 때
            post.like.remove(user) #like field에 현재 유저 추가
            message = "좋아요 취소" #화면에 띄울 메세지
        else: #좋아요를 누르지 않은 유저일 때
            post.like.add(user) #like field에 현재 유저 삭제
            message = "좋아요" #화면에 띄울 메세지
        # post.like.count() : 게시물이 받은 좋아요 수  
        context = {'like_count' : post.like.count(),"message":message}
        return HttpResponse(json.dumps(context), content_type='application/json')   


#게시글 
def notice_board(request, notice_id):
    notice_detail = get_object_or_404(Notice, pk=notice_id)
    return render(request, 'notice_board.html', {'notice':notice_detail})

  
