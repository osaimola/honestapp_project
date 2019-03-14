from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinLengthValidator
from django.utils import timezone
from django.template.defaultfilters import slugify
import datetime


# Create your models here.
class Category(models.Model):
    category = models.CharField(max_length=100, unique=True, default='General',
                                help_text="Category of Service Provided")
    views = models.IntegerField(default=0)
    slug = models.SlugField()

    def save(self, *args, **kwargs):
        """override save function to add a slug on creationm updates slug on namechange"""
        self.slug = slugify(self.category)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.category


class Area(models.Model):
    state = models.CharField(max_length=100, unique=True, default='Nigeria')
    views = models.IntegerField(default=0)
    slug = models.SlugField()
    """ commented out, states are unique and cant have multiple areas
    area = models.CharField(max_length=100, unique=True, null=True)
    """

    def save(self, *args, **kwargs):
        """override save function to add a slug on creationm updates slug on namechange"""
        self.slug = slugify(self.state)
        super(Area, self).save(*args, **kwargs)

    def __str__(self):
        return self.state


class Person(models.Model):
    service = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='service', help_text='Service')
    location = models.ForeignKey(Area, on_delete=models.PROTECT, related_name='location', help_text='Location (state)')
    first_name = models.CharField(max_length=60, help_text='First name')
    last_name = models.CharField(max_length=60, help_text='Last name (surname)')
    phone_number = models.CharField(max_length=14, validators=[
        MinLengthValidator(11, message='phone number must be 11 - 14 characters long')], help_text="phone number 11"
                                                                                                   "- 14 digits allowed")
    email = models.EmailField(max_length=150, blank=True, help_text='Valid email address')
    date_added = models.DateField(auto_now_add=True)
    views = models.IntegerField(default=0)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    rating = models.FloatField(default=0)

    def __str__(self):
        return self.first_name

    def recently_added(self):
        """returns true if this person was added within the last 10 days"""
        now = timezone.now()
        return now - datetime.timedelta(days=10) <= self.date_added <= now

    def vote_positive(self):
        """return the weight of all votes, positive if upvotes are more, negative if downvotes are more"""
        return self.upvotes > self.downvotes

    #def set_average_rating(self):



class UserProfile(User):

    def __str__(self):
        return self.username


class Review(models.Model):
    ONE_STAR = 1
    TWO_STARS = 2
    THREE_STARS = 3
    FOUR_STARS = 4
    FIVE_STARS = 5

    CHOICE_SET = (
        (ONE_STAR, "1 Star"),
        (TWO_STARS, "2 Stars"),
        (THREE_STARS, "3 Stars"),
        (FOUR_STARS, "4 Stars"),
        (FIVE_STARS, "5 Stars"),
    )
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="person")
    reviewer = models.ForeignKey(UserProfile ,on_delete=models.CASCADE, blank=True, null=True, related_name="reviewer")
    rating = models.IntegerField(default=5, choices=CHOICE_SET)
    summary = models.CharField(max_length=40)
    review_text = models.CharField(max_length=360, blank=True)

    def __str__(self):
        return self.summary