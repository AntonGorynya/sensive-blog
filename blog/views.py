from django.shortcuts import render
from django.db import connection
from blog.models import Comment, Post, Tag
from django.db.models import Count


def serialize_post_optimized(post):
    #tags = post.tags.all()
    tags = Tag.objects.filter(posts=post).popular().fetch_with_posts()
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag_optimized(tag) for tag in tags],
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
    most_popular_posts = Post.objects.popular()[:5].comments().prefetch_related('author').prefetch_related('tags')
    most_popular_tags = Tag.objects.popular()[:5]
    most_fresh_posts = Post.objects.fresh()[:5].prefetch_related('author').prefetch_related('tags')
    context = {
        'most_popular_posts': [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post_optimized(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag_optimized(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    #post = Post.objects.get(slug=slug)
    post = Post.objects.filter(slug=slug).comments().popular()[0]
    print(post)

    comments = Comment.objects.filter(post=post)
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    related_tags = post.tags.all()

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': post.likes_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in related_tags],
    }


    most_popular_tags = Tag.objects.popular()[:5]
    most_popular_posts = Post.objects.popular()[:5].comments().prefetch_related('author').prefetch_related('tags')

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
    most_popular_posts = Post.objects.popular()[:5].comments().prefetch_related('author').prefetch_related('tags')
    related_posts = tag.posts.popular()[:20].comments().prefetch_related('author').prefetch_related('tags')

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag_optimized(tag) for tag in most_popular_tags],
        'posts': [serialize_post_optimized(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
