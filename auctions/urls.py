from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    path("", views.ListingListView.as_view(), name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add_listing", views.add_auction, name="add_listing"),
    path("<int:listing_id>", views.listing, name="listing"),
    path("wishlist", login_required(views.WishlistListView.as_view()), name="wishlist"),
    path("comment", views.comment, name="comment"),
    path('categories', views.categories, name='categories'),
    path('<str:category>-category', views.CategoryListingListView.as_view(), name='category'),
    path('mylistings', views.UserListingListView.as_view(), name='mylistings'),
    path('closelisting-<int:listing_id>', views.close_listing, name='closelisting')
]
