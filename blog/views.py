from django.shortcuts import render
from django.db import connection
from blog.models import Comment, Post, Tag


def get_related_posts_count(tag):
    return tag.posts.count()

def get_likes_count(post):
    return post.likes.count()


def get_most_popular_posts(Post):
    popular_posts = Post.objects.all()
    return sorted(popular_posts, key=get_likes_count)


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


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': len(Post.objects.filter(tags=tag)),
    }


def index(request):
    most_popular_posts = get_most_popular_posts(Post)[-5:]
    #get_most_popular_posts_v2(Post)

    fresh_posts = Post.objects.order_by('published_at')
    most_fresh_posts = list(fresh_posts)[-5:]

    tags = Tag.objects.all()
    popular_tags = sorted(tags, key=get_related_posts_count)
    most_popular_tags = popular_tags[-5:]

    context = {
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
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

    all_tags = Tag.objects.all()
    popular_tags = sorted(all_tags, key=get_related_posts_count)
    most_popular_tags = popular_tags[-5:]

    most_popular_posts = []  # TODO. Как это посчитать?

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    all_tags = Tag.objects.all()
    popular_tags = sorted(all_tags, key=get_related_posts_count)
    most_popular_tags = popular_tags[-5:]

    most_popular_posts = []  # TODO. Как это посчитать?

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
