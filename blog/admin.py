from django.contrib import admin
from blog.models import Post, Tag, Comment


@admin.register(Comment)
class CommentForm(admin.ModelAdmin):
    list_display = ['post', 'author', 'published_at']
    raw_id_fields = ['author', 'post']


@admin.register(Post)
class PostForm(admin.ModelAdmin):
    raw_id_fields = ['author', 'likes', 'tags']


@admin.register(Tag)
class TagForm(admin.ModelAdmin):
    pass
