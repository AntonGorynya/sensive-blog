from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Count, Prefetch


class PostQuerySet(models.QuerySet):

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

    def fetch_author_tag(self, popular_tags):
        return self.select_related('author').prefetch_related(Prefetch('tags', queryset=popular_tags))


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

    objects = PostQuerySet.as_manager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args={'slug': self.slug})

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'


class Tag(models.Model):
    title = models.CharField('Тег', max_length=20, unique=True)
    objects = TagQuerySet.as_manager()

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
