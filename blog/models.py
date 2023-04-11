from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Count


class PostQuerySet(models.QuerySet):
    def year(self, year):
        posts_at_year = self.filter(published_at__year=year).order_by('published_at')
        return posts_at_year

    def fresh(self):
        most_fresh_posts = Post.objects.annotate(comments_count=Count('comments')).order_by(
            '-published_at')
        return most_fresh_posts
    # def fetch
    #     ids_and_comments = most_fresh_posts.values_list('id', 'comments_count')
    #     count_for_comments = dict(ids_and_comments)
    #     for post in most_fresh_posts:
    #         post.comments_count = count_for_comments[post.id]
    #     return most_fresh_posts
    def popular(self):
        posts_with_likes = Post.objects.annotate(likes_count=Count('likes')).order_by('-likes_count')
        return posts_with_likes

    def fetch_with_comments_count(self):
        posts_with_likes = self
        most_popular_posts_ids = [post.id for post in posts_with_likes]
        posts_with_comments = Post.objects.filter(id__in=most_popular_posts_ids).annotate(
            comments_count=Count('comments'))
        ids_and_comments = posts_with_comments.values_list('id', 'comments_count')
        ids_and_likes = posts_with_likes.values_list('id', 'likes_count')
        count_for_comments = dict(ids_and_comments)
        count_for_likes = dict(ids_and_likes)
        for post in posts_with_likes:
            post.comments_count = count_for_comments[post.id]
            post.likes_count = count_for_likes[post.id]
        return posts_with_likes


class TagQuerySet(models.QuerySet):
    def popular(self):
        most_popular_tags = Tag.objects.annotate(num_posts=Count('posts')).order_by('-num_posts')
        return most_popular_tags

        # ids_and_posts = most_popular_tags.values_list('id', 'num_posts')
        # count_for_posts = dict(ids_and_posts)
        # for tag in most_popular_tags:
        #     tag.num_posts = count_for_posts[tag.id]
        # return most_popular_tags


class Post(models.Model):
    objects = PostQuerySet.as_manager()
    title = models.CharField('Заголовок', max_length=200)
    text = models.TextField('Текст')
    slug = models.SlugField('Название в виде url', max_length=200)
    image = models.ImageField('Картинка')
    published_at = models.DateTimeField('Дата и время публикации')

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        limit_choices_to={'is_staff': True})
    likes = models.ManyToManyField(
        User,
        related_name='liked_posts',
        verbose_name='Кто лайкнул',
        blank=True)
    tags = models.ManyToManyField(
        'Tag',
        related_name='posts',
        verbose_name='Теги')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args={'slug': self.slug})

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'


class Tag(models.Model):
    objects = TagQuerySet.as_manager()
    title = models.CharField('Тег', max_length=20, unique=True)

    def __str__(self):
        return self.title

    def clean(self):
        self.title = self.title.lower()

    def get_absolute_url(self):
        return reverse('tag_filter', args={'tag_title': self.slug})

    class Meta:
        ordering = ['title']
        verbose_name = 'тег'
        verbose_name_plural = 'теги'


class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        verbose_name='Пост, к которому написан',
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )

    text = models.TextField('Текст комментария')
    published_at = models.DateTimeField('Дата и время публикации')

    def __str__(self):
        return f'{self.author.username} under {self.post.title}'

    class Meta:
        ordering = ['published_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
