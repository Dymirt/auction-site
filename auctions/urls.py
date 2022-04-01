from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add_listing", views.add_auction, name="add_listing"),
    path("<int:listing_id>", views.listing, name="listing"),
    path("wishlist", views.wishlist, name="wishlist"),
    path("comment", views.comment, name="comment")
]
