from django.forms import ModelForm, NumberInput, HiddenInput

from .models import Listing,  Bid, Comment


class ListingForm(ModelForm):

    class Meta:
        model = Listing
        fields = ['category', 'title', 'description', 'starting_bid', 'image_url']
        widgets = {
            'starting_bid': NumberInput(attrs={'min': 0, 'step': 0.01}),
        }


class BidForm(ModelForm):



    class Meta:

        model = Bid
        fields = ['bid', 'user', 'listing']
        widgets = {
            'bid': NumberInput(attrs={'step': 0.01, 'min': 0}),
            'user': HiddenInput(),
            'listing': HiddenInput(),
        }

        def __init__(self, min_bid):
            min_bid = min_bid




class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['user', 'listing', 'text']
