import datetime

from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone

STATUS = (
    (0, "Draft"),
    (1, "Publish")
)


class Post(models.Model):
    post_id = models.PositiveIntegerField(default=1, blank=True, null=True)
    text = models.CharField(max_length=500,
                            editable=True, unique=False, default='Basketball Trip Meetday',
                            help_text='Basketball Trip Meetday')
    meet_day = models.DateField(default=datetime.date.today, null=False, blank=False, unique=True,
                                error_messages={
                                    'unique': "There cannot be 2 trips meetings on the same date. A player has already created a trip for others to sign up on this day. Check out feed list page for all BBall meetings on weekdays."})
    content = models.TextField(
        default=' Join pickup basketball trips to street basketball courts in Oslo, Norway',
        editable=False)
    created_on = models.DateTimeField(default=datetime.date.today)
    likes = models.IntegerField(default=0)
    user_likes = models.ManyToManyField(User, related_name="user_likes")

    url = models.SlugField(max_length=500, unique=True, blank=True, null=True, editable=False,
                           help_text='If blank, the slug will be generated automatically from given ..')
    status = models.IntegerField(choices=STATUS, default=0)
    created_by_user = models.ForeignKey(User, on_delete=models.CASCADE, default=0)

    def save(self, *args, **kwargs):
        self.url = slugify(self.meet_day)
        super(Post, self).save(*args, **kwargs)

    def all_users(self):
        return self.user_likes.all()

    @property
    def total_likes(self):
        return self.user_likes.count()

    class Meta:
        ordering = ['-meet_day']




LIKE_CHOICES = (
    ('Im Coming & Playing this day (Sign Up)', 'Im Coming & Playing this day (Sign Up)'),
    ('You are already Signed up to join. Change your presence -> (Sign out)',
     'You are already Signed up to join. Change your presence -> (Sign out)'),
)


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="users")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="posts")
    alreadyLiked = models.BooleanField(default=False)
    value = models.CharField(choices=LIKE_CHOICES, max_length=80, default="Im Coming & Playing this day (Sign Up)")
    created = models.DateTimeField(default=timezone.now)
