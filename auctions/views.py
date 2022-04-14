from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User, Listing, Category, Comment
from .forms import ListingForm, BidForm, CommentForm
from django.views.generic.list import ListView


class ListingListView(ListView):
    model = Listing
    paginate_by = 10
    template_name = "auctions/listings.html"
    title = "Listings"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def add_auction(request):
    if request.method == "GET":
        Listing_form = ListingForm(initial={'user': request.user})

    else:
        Listing_form = ListingForm(request.POST)
        if Listing_form.is_valid():
            listing = Listing_form.save()
            return HttpResponseRedirect(reverse('listing', kwargs={'listing_id': listing.pk}))

    return render(request, "auctions/add_listing.html", {'form': Listing_form})


def listing(request, listing_id):

    listing = Listing.objects.get(pk=listing_id)

    # Bid form initialization
    bid_form = BidForm(initial={'user': request.user.id, 'listing': listing})

    if listing.bids.all():
        min_bid = float(listing.highest_bid().bid) + bid_form.fields['bid'].widget.attrs['step']
    else:
        min_bid = float(listing.starting_bid)

    bid_form.fields['bid'].widget.attrs['min'] = min_bid

    # Comment form initialization
    comment_form = CommentForm(initial={'user': request.user.id, 'listing': listing})

    context = {
        'comment_form': comment_form,
        'bid_form': bid_form,
        'listing': listing
    }

    if request.method == "POST":
        form = BidForm(request.POST)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.bid = float(bid.bid)
            if bid.bid >= min_bid:
                bid.save()
        return HttpResponseRedirect(reverse('listing', kwargs={'listing_id': listing_id}))
    else:
        return render(request, "auctions/listing_detail.html", context)


@login_required
def comment(request):
    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment_form.save()
        return HttpResponseRedirect(reverse('listing', kwargs={'listing_id': request.POST['listing']}))


class WishlistListView(ListingListView):
    title = "Wishlist"

    def get_queryset(self):
        return self.request.user.wishlist.all()

    def post(self, request):
        listing = self.model.objects.get(pk=request.POST['listing_id'])
        if listing not in request.user.wishlist.all():
            request.user.wishlist.add(listing)
        else:
            request.user.wishlist.remove(listing)
        return HttpResponseRedirect(reverse('listing', kwargs={'listing_id': request.POST['listing_id']}))


def categories(request):
    categories_list = Category.objects.all()
    return render(request, "auctions/categories.html", {'categories': categories_list})


class CategoryListingListView(ListingListView):
    model = Category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.kwargs['category']
        return context

    def get_queryset(self):
        category = self.model.objects.get(title=self.kwargs['category'])
        return category.listings.all()


class UserListingListView(ListingListView):
    title = 'My listings'

    def get_queryset(self):
        return self.request.user.listings.all()


@login_required
def close_listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)

    if request.method == "POST" and request.user == listing.user:
        listing.is_active = False
        listing.save()
        return HttpResponseRedirect(reverse('listing', kwargs={'listing_id': listing_id}))