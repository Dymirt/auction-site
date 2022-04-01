from django.forms import ModelForm
from .models import Listing, Comment


class ListingForm(ModelForm):

    class Meta:
        model = Listing
        fields = ['category', 'title', 'description', 'starting_bid']


class CommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ['text']