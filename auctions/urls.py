from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("nonActive", views.non_active_listings, name="non_active_listings"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createlisting",views.create_listing,name="create_lisiting"),
    path("categories",views.categories,name="categories"),
    path("category",views.category,name="category"),
    path("listing/<int:id>",views.listing_page,name="listing_page"),
    path("watchlist",views.watchlist,name="watchlist"),
    path("bid/<int:id>",views.bid,name="bid"),
    path("closeBid/<int:listing_id>",views.close_bid,name="close_bid"),
    path("addcomment/<int:listing_id>",views.add_comment,name="add_comment")
]
