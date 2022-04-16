from django.contrib.auth.models import AbstractUser
from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=20)

    def __str__(self):
        return self.title


class Bid(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='bids')
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='bids')
    bid = models.DecimalField(decimal_places=2, max_digits=10)


class Comment(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='comments')
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='comments')
    date = models.DateTimeField(auto_now=True)
    text = models.TextField()


def image_path(instance, filename):
    return 'listing_img/user_{0}//{1}'.format(instance.user.id, filename)


class Listing(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='listings')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=60)
    description = models.TextField(max_length=500)
    starting_bid = models.DecimalField(decimal_places=2, max_digits=10)
    is_active = models.BooleanField(default=True)
    image_url = models.URLField(blank=True, null=True)
    date = models.DateTimeField(auto_now=True)

    def highest_bid(self):
        try:
            return max(self.bids.all(), key=lambda x: x.bid)
        except ValueError:
            return None

    class Meta:
        ordering = ['pk']


class User(AbstractUser):
    wishlist = models.ManyToManyField(Listing, blank=True, related_name="followers")

