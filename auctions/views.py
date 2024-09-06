from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from decimal import Decimal
from .models import *

from .models import User


def index(request):
    active_listings = Listing.objects.filter(state=True).all()
    return render(request, "auctions/index.html",{
        "listings" : active_listings,
        "state" : "Active"
    })

def non_active_listings(request):
    non_active_listings = Listing.objects.filter(state=False).all()
    return render(request, "auctions/index.html",{
        "listings" : non_active_listings,
        "state" : "Non-Active"
    })


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

def create_listing(request):
    if request.user.is_authenticated:
        categories = Listing._meta.get_field('category').choices
        if request.method == "POST":
            title = request.POST.get("title")
            description = request.POST.get("description")
            starting_bid = request.POST.get("starting_bid")
            category=request.POST.get("category", "")
            image = request.FILES.get('image', None)    

            user = request.user
            starting_bid = Bid(
                owner=user,
                price=starting_bid
            )
            starting_bid.save()

            listing = Listing(
                title=title,
                description=description,
                starting_bid=starting_bid,
                category=category if category else None,
                image=image,
                owner=user
            )
            listing.save()
            active_listings = Listing.objects.filter(state=True).all()
            return render(request,"auctions/listing.html",{
                "listing" : listing
            })  
        else :
            return render(request, "auctions/create_listing.html",
            {
                "categories" : categories
            })


def categories(request):
    return render(request, "auctions/categories.html",{
        "categories" : Listing._meta.get_field('category').choices
    })

def category(request):
    if request.method == "POST":
        category = request.POST.get("category")
        active_listings = Listing.objects.filter(category=category).all()
        return render(request,"auctions/category.html",{
            "category" : category,
            "active_listings" : active_listings
        })

def listing_page(request,id):
    listing_id = id
    listing = Listing.objects.get(id=listing_id)
    return render(request,"auctions/listing.html",{
            "listing" : listing
        })

def watchlist(request):
    user = request.user
    if request.method == "POST":
        listing_id = request.POST.get("listing_id")
        listing = Listing.objects.get(id=listing_id)

        # Toggle the watchlist status
        if listing in user.watchlist.all():
            user.watchlist.remove(listing)
        else:
            user.watchlist.add(listing)

    user_watchlist = user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "user_watchlist": user_watchlist
    })

def bid(request,id):
    if request.user.is_authenticated:
        listing = Listing.objects.get(id=id)
        listing_owner = listing.owner.id
        current_user = request.user
        if listing_owner == current_user:
            return
        if request.method == "POST":
                new_bid_price = Decimal(request.POST.get("current_bid"))
                if listing.current_bid :
                    current_bid_price = listing.current_bid.price
                    if new_bid_price > current_bid_price and new_bid_price >= listing.starting_bid.price :
                        new_bid = Bid(
                            price=new_bid_price,
                            owner=current_user
                        )
                        new_bid.save()
                        listing.current_bid.delete()
                        listing.current_bid = new_bid
                        listing.save()
                        return render(request, "auctions/listing.html",{
                            "listing" : listing
                        })
                    else :
                        return render(request, "auctions/listing.html",{
                            "listing" : listing,
                            "error_message" : "Your bid should be higher than the current Bid"
                        })
                else :
                    new_bid = Bid(
                            price=new_bid_price,
                            owner=current_user
                    )
                    new_bid.save()
                    listing.current_bid = new_bid
                    listing.save()
                    return render(request, "auctions/listing.html",{
                            "listing" : listing
                    })

def close_bid(request,listing_id):
    current_listing = Listing.objects.get(id=listing_id)
    if not request.user.is_authenticated or request.user != current_listing.owner or current_listing.state == False :
        return
    if request.method == "POST" :     
        current_listing.state = False
        current_listing.save()
        return render(request, "auctions/listing.html", {
          "listing" : current_listing  
        })

def add_comment(request,listing_id):
    if not request.user.is_authenticated :
        return render(request,"auctions/login.html")
    if request.method == "POST":
        comment_content = request.POST.get("comment")
        commnet_owner = request.user
        comment_listing = Listing.objects.get(id=listing_id)
        comment = Comment(
            listing=comment_listing,
            content=comment_content,
            owner=commnet_owner
        )
        comment.save()
        return render(request, "auctions/listing.html", {
          "listing" : comment_listing,
        })

