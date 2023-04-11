from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Count


class PostQuerySet(models.QuerySet):
    def year(self, year):
        posts_at_year = self.filter(published_at__year=year).order_by('published_at')
        return posts_at_year

    def fresh(self):
        most_fresh_posts = self.annotate(comments_count=Count('comments')).order_by(
            '-published_at')
        return most_fresh_posts

    def popular(self):
        posts_with_likes = self.annotate(likes_count=Count('likes', distinct=True)).order_by('-likes_count')
        return posts_with_likes

    def comments(self):
        ids = [post.id for post in self]
        posts_with_comments = Post.objects.filter(id__in=ids).annotate(comments_count=Count('comments'))
        return posts_with_comments

    def fetch_with_comments_count(self):
        ids_and_comments = self.values_list('id', 'comments_count')
        count_for_comments = dict(ids_and_comments)
        for post in self:
            post.comments_count = count_for_comments[post.id]
        return self

    def fetch_likes_count(self):
        ids_and_likes = self.values_list('id', 'likes_count')
        count_for_likes = dict(ids_and_likes)
        for post in self:
            post.likes_count = count_for_likes[post.id]
        return self


class TagQuerySet(models.QuerySet):
    def popular(self):
        most_popular_tags = self.annotate(num_posts=Count('posts')).order_by('-num_posts')
        return most_popular_tags
    def fetch_with_posts(self):
        ids_and_posts = self.values_list('id', 'num_posts')
        count_for_posts = dict(ids_and_posts)
        for tag in self:
            tag.num_posts = count_for_posts[tag.id]
        return self


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
