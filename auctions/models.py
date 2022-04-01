from django.contrib.auth.models import AbstractUser
from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=20)
    listings = models.ManyToManyField('Listing', blank=True, related_name='categories')

    def __str__(self):
        return self.title


class Bid(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, blank=True)
    bid = models.FloatField()


class Comment(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    text = models.TextField()


class Listing(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    starting_bid = models.FloatField()
    bids = models.ManyToManyField(Bid, blank=True, related_name='bidders')
    comments = models.ManyToManyField(Comment, blank=True, related_name='commenters')
    active = models.BooleanField(default=True)
    winner = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='victories')
    # TODO add photo field
    # image = models.ImageField()

    def highest_bid(self):
        if self.bids:
            try:
                return max(self.bids.all(), key=lambda x: x.bid)
            except ValueError:
                return None


class User(AbstractUser):
    watchlist = models.ManyToManyField(Listing, blank=True, related_name="followers")

