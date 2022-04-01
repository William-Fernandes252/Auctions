from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.utils.timezone import now, timedelta, datetime
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from authentication.models import User
from .managers import ListingQuerySet


class Category(models.Model):
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ('-name',)
    
    name = models.CharField(max_length=32, unique=True)
    def __str__(self):
        return self.name.title()


class Listing(models.Model):
    objects = ListingQuerySet.as_manager()
        
    DURATIONS = (
        (3, "Three days"),
        (7, "One week"),
        (14, "Two weeks"),
        (30, "One month")
    )
    
    author = models.ForeignKey(User, related_name="listings", on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=1000, blank=True)
    initial_price = models.DecimalField(
        max_digits=9, 
        decimal_places=2, 
        validators= [MinValueValidator(0.01, "The price must be a positive value.")]
    )
    image = ProcessedImageField(
        blank=True, 
        upload_to='auctions/%Y/%m/%d', 
        processors=[
            ResizeToFill(500, 500)
        ],
        format='JPEG',
        options={'quality': 100}
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category')
    watchers = models.ManyToManyField(User, blank=True, related_name="watchlist")
    creation_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()
    duration = models.IntegerField(choices=DURATIONS)
    ended_manually = models.BooleanField(default=False)
    public = models.BooleanField(default=True)
    winner = models.ForeignKey(User, blank=True, related_name="wins", on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ('creation_time',) 
        
    def __str__(self):
        return f"{self.title} ({self.author.username})"
    
    def save(self, *args, **kwargs):
        self.creation_time = now()
        self.end_time = self.creation_time + timedelta(days=self.duration)
        super().save(*args, **kwargs)
        
    def is_finished(self):
        return self.ended_manually or self.end_time < timezone.now()
    
    def is_valid_listing(self):
        return self.duration > 0 and self.end_time != self.creation_time and self.initial_price > 0.00


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name = "bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "bids")
    creation_time = models.DateTimeField(auto_now_add=True)
    value = models.DecimalField(max_digits=9, decimal_places=2)
    
    class Meta:
        ordering = ('-value',)
        
    def __str__(self):
        return f"Bid #{self.id} on {self.listing.title} by {self.user.username}"
    
    
class Answer(models.Model):
    author = models.ForeignKey(User, related_name="author", on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    body = models.TextField(max_length=250)
    
    def __str__(self):
        return f"{self.author} {((now() - self.time).total_seconds()//3600):.0f} hours ago: {self.body}"
    
        
class Question(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name = "questions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "questions")
    time = models.DateTimeField(auto_now_add=True)
    body = models.TextField(max_length=250)
    answer = models.OneToOneField(Answer, on_delete=models.CASCADE, related_name="question", null=True, blank=True)
    
    class Meta:
        ordering = ('-time',)
    
    def __str__(self):
        return f"{self.user} {((now() - self.time).total_seconds()//3600):.0f} hours ago: {self.body}"