from django.shortcuts import render
from django.db import connection
from blog.models import Comment, Post, Tag
from django.db.models import Count


def get_most_popular_posts_v2(Post):
    cursor = connection.cursor()
    cursor.execute('''SELECT  post_id , COUNT(*) as likes FROM blog_post_likes bpl 
                      GROUP BY post_id 
                      ORDER BY likes DESC
                      limit 5'''
    )
    popular_posts = []
    for raw in cursor.fetchall():
        popular_posts.append(Post.objects.get(id=raw[0]))
    return popular_posts


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': len(Comment.objects.filter(post=post)),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_post_optimized(post):
    tags = post.tags.all()
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in tags],
        'first_tag_title': tags[0].title,
    }


def serialize_tag_optimized(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.num_posts,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': Post.objects.filter(tags=tag).count(),
    }


def index(request):
    most_popular_posts = Post.objects.popular().prefetch_related('author')[:5].fetch_with_comments_count()
    most_popular_tags = Tag.objects.popular()[:5]
    most_fresh_posts = Post.objects.fresh().prefetch_related('author')[:5]
    context = {
        'most_popular_posts': [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post_optimized(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag_optimized(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = Post.objects.get(slug=slug)
    comments = Comment.objects.filter(post=post)
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    likes = post.likes.count()

    related_tags = post.tags.all()

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': likes,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in related_tags],
    }

    most_popular_tags = Tag.objects.popular()[:5]
    most_popular_posts = Post.objects.popular().prefetch_related('author')[:5].fetch_with_comments_count()

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    most_popular_tags = Tag.objects.popular()[:5]
    most_popular_posts = Post.objects.popular().prefetch_related('author')[:5].fetch_with_comments_count()

    related_posts = tag.posts.all()[:20]

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag_optimized(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
