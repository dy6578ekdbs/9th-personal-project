from django.db import models
from django.utils import timezone
from account.models import CustomUser
from django.conf import settings
# Create your models here.

class HashTag(models.Model):
    hashtag_name = models.CharField(max_length=100)

    def __str__(self):
        return self.hashtag_name

class Blog(models.Model): #큰 글
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=200)
    pub_date = models.DateField('date published')
    body =models.TextField()
    hashtag = models.ManyToManyField(HashTag) #해시태그
    like = models.ManyToManyField(CustomUser, related_name='likes',blank=True)
    cover_image= models.ImageField(upload_to='images/', blank=True, null=True)

    def __str__(self):
        return self.title
    
    def summary(self):
        return self.body[:30]

class Youtube(models.Model): #하위 유튜브 목록
    post = models.ForeignKey(Blog, related_name='youtubes', on_delete=models.CASCADE)
    subtitle = models.CharField(max_length=200)
    body = models.TextField()
    url = models.CharField(null=True, max_length=500)
    
    def apporve(self):
        self.save()

    def __str__(self):
        return self.subtitle

class Comment(models.Model):
    post = models.ForeignKey(Blog, related_name='comments', on_delete=models.CASCADE)
    author_name = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    comment_text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def apporve(self):
        self.save()

    def __str__(self):
        return self.comment_text

class Notice(models.Model):
    notice_title = models.CharField(max_length=100)
    notice_pub_date = models.DateField('date published')
    notice_body = models.TextField()

    def __str__(self):
        return self.notice_title
    
    def notice_summary(self):
        return self.notice_body[:20]