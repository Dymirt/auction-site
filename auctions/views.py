from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User, Listing, Category, Comment
from .forms import ListingForm, BidForm
from django.views.generic.list import ListView


class ListingListView(ListView):
    model = Listing
    paginate_by = 10
    template_name = "auctions/listings.html"
    title = "Active Listings"

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
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.user = request.user
            listing.save()

        return HttpResponseRedirect(reverse("index"))

    else:
        form = ListingForm(initial={'user': request.user.id})
        return render(request, "auctions/add_listing.html", {'form': form})


def listing(request, listing_id):

    listing = Listing.objects.get(pk=listing_id)

    form = BidForm(initial={'user': request.user.id, 'listing': listing})

    if listing.bids.all():
        highest_bid = listing.highest_bid()
        min_bid = highest_bid.bid + form.fields['bid'].widget.attrs['step']
    else:
        min_bid = listing.starting_bid

    if request.method == "GET":

        form.fields['bid'].widget.attrs['min'] = min_bid
        context = {
            'listing': listing,
            'form': form
        }

        if request.user.is_authenticated:
            if request.user.watchlist.filter(pk=listing_id):
                context['wishlist'] = True
        return render(request, "auctions/listing_view.html", context)

    else:
        form = BidForm(request.POST)
        if form.is_valid():
            bid = form.save(commit=False)
            if bid.bid >= min_bid:
                bid.save()
                listing.bids.add(bid)
                return HttpResponseRedirect(reverse('listing', kwargs={'listing_id': listing_id}))


@login_required
def comment(request):
    if request.method == "POST":
        listing = Listing.objects.get(pk=request.POST.get('listing_id'))
        comment = Comment()
        comment.user = request.user
        comment.listing = listing
        comment.text = request.POST.get('comment')
        comment.save()
        listing.comments.add(comment)
        return HttpResponseRedirect(reverse('listing', kwargs={'listing_id': request.POST.get('listing_id')}))


def wishlist(request):
    title = "Wishlist"

    if request.method == "POST":
        listing = Listing.objects.get(pk=request.POST['listing_id'])

        if listing not in request.user.watchlist.all():
            request.user.watchlist.add(listing)
        else:
            request.user.watchlist.remove(listing)
        return HttpResponseRedirect(reverse('listing', kwargs={'listing_id': request.POST['listing_id']}))
    else:
        listings = request.user.watchlist.all().filter(is_active=True)
        return render(request, "auctions/listings.html", {
            'object_list': listings,
            'title': title
        })


class WishlistListView(ListingListView):
    title = "Wishlist"

    def get_queryset(self):
        return self.request.user.watchlist.all()

    def post(self, request):
        listing = self.model.objects.get(pk=request.POST['listing_id'])
        if listing not in request.user.watchlist.all():
            request.user.watchlist.add(listing)
        else:
            request.user.watchlist.remove(listing)
        return HttpResponseRedirect(reverse('listing', kwargs={'listing_id': request.POST['listing_id']}))


def categories(request):
    categories_list = Category.objects.all()
    return render(request, "auctions/categories.html", {'categories': categories_list})


def category_listings(request, category):
    category = Category.objects.get(title=category)
    listings = Listing.objects.all().filter(category=category, is_active=True)
    return render(request, "auctions/listings.html", {
        'object_list': listings,
        'title': category
    })


class UserListingListView(ListingListView):
    title = 'My listings'

    def get_queryset(self):
        return self.model.objects.all().filter(user=self.request.user)

@login_required
def close_listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)

    if request.user == listing.user and request.method == "POST":
        listing.is_active = False
        listing.save()
        return HttpResponseRedirect(reverse('listing', kwargs={'listing_id': listing_id}))