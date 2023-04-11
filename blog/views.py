from django.shortcuts import render
from django.db import connection
from blog.models import Comment, Post, Tag
from django.db.models import Count


def get_most_popular_posts(Post):
    posts_with_likes = Post.objects.annotate(likes_count=Count('likes')).order_by('-likes_count').prefetch_related('author')[:5]
    most_popular_posts_ids = [post.id for post in posts_with_likes]
    posts_with_comments = Post.objects.filter(id__in=most_popular_posts_ids).annotate(comments_count=Count('comments'))
    ids_and_comments = posts_with_comments.values_list('id', 'comments_count')
    ids_and_likes = posts_with_likes.values_list('id', 'likes_count')
    count_for_comments = dict(ids_and_comments)
    count_for_likes = dict(ids_and_likes)
    for post in posts_with_likes:
        post.comments_count = count_for_comments[post.id]
        post.likes_count = count_for_likes[post.id]
    return posts_with_likes


def get_most_fresh_posts(Post):
    most_fresh_posts = Post.objects.annotate(comments_count=Count('comments')).order_by('-published_at').prefetch_related('author')[:5]
    ids_and_comments = most_fresh_posts.values_list('id', 'comments_count')
    count_for_comments = dict(ids_and_comments)
    for post in most_fresh_posts:
        post.comments_count = count_for_comments[post.id]
    return most_fresh_posts


def get_most_popular_tags(Tag):
    most_popular_tags = Tag.objects.annotate(num_posts=Count('posts')).order_by('-num_posts')[:5]
    ids_and_posts = most_popular_tags.values_list('id', 'num_posts')
    count_for_posts = dict(ids_and_posts)
    for tag in most_popular_tags:
        tag.num_posts = count_for_posts[tag.id]
        print(tag, tag.num_posts)
    return most_popular_tags


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
    #print(Comment.objects.filter(post=post).count())
    #print(post.num_comments)
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_tag_optimized(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.num_posts,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': len(Post.objects.filter(tags=tag)),
    }


def index(request):
    most_popular_posts = get_most_popular_posts(Post)
    most_popular_tags = get_most_popular_tags(Tag)
    most_fresh_posts = get_most_fresh_posts(Post)
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

    likes = post.likes.all()

    related_tags = post.tags.all()

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': len(likes),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in related_tags],
    }

    most_popular_tags = get_most_popular_tags(Tag)
    most_popular_posts = get_most_popular_posts(Post)

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

    most_popular_tags = get_most_popular_tags(Tag)
    most_popular_posts = get_most_popular_posts(Post)

    related_posts = tag.posts.all()[:20]

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
