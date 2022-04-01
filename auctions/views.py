from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User, Listing, Category, Bid, Comment
from .forms import ListingForm


def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html", {'listings': listings})


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
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = Listing()
            listing.user = request.user
            listing.category = Category.objects.get(pk=form.data['category'])
            listing.title = form.data['title']
            listing.description = form.data['description']
            listing.starting_bid = form.data['starting_bid']
            listing.save()
        return HttpResponseRedirect(reverse("index"))

    else:
        form = ListingForm(initial={'user': request.user.id})
        return render(request, "auctions/add_listing.html", {'form': form})


def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    context = {'listing': listing}

    if request.method == "POST":
        bid_value = float(request.POST['bid'])
        if listing.highest_bid():
            if bid_value > listing.highest_bid().bid:
                bid = Bid(user=request.user, auction=listing, bid=bid_value)
                bid.save()
                listing.bids.add(bid)

    if listing.bids.all():
        context['highest_bid'] = listing.highest_bid()
        context['bids'] = listing.bids.all().order_by('-bid')[:3]
    if request.user.is_authenticated:
        if request.user.watchlist.filter(pk=listing_id):
            context['wishlist'] = True
    return render(request, "auctions/listing_view.html", context)


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
        print('Hello new comment')
        return HttpResponseRedirect(reverse('listing', kwargs={'listing_id': request.POST.get('listing_id')}))


@login_required
def wishlist(request):

    if request.method == "POST":
        listing = Listing.objects.get(pk=request.POST['listing_id'])

        if listing not in request.user.watchlist.all():
            request.user.watchlist.add(listing)
        else:
            request.user.watchlist.remove(listing)
        return HttpResponseRedirect(reverse('listing', kwargs={'listing_id': request.POST['listing_id']}))
    else:
        listings = request.user.watchlist.all()
        return render(request, "auctions/wishlist.html", {'listings': listings})

