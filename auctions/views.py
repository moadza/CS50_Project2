from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import *

from .models import User


def index(request):
    active_listings = Listing.objects.filter(active=True).all()
    return render(request, "auctions/index.html",{
        "active_listings" : active_listings
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
    categories = Listing._meta.get_field('category').choices
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        starting_bid = request.POST.get("starting_bid")
        category=request.POST.get("category", "")
        active = 'active' in request.POST
        image = request.FILES.get('image', None)

        listing = Listing(
            title=title,
            description=description,
            starting_bid=starting_bid,
            category=category if category else None,
            active=active,
            image=image,
            owner=request.user
        )
        listing.save()
        active_listings = Listing.objects.filter(active=True).all()
        return render(request, "auctions/index.html",{
            "active_listings" : active_listings
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

def listing_page(request,title):
    listing_title = title
    listing = Listing.objects.get(title=listing_title)
    if request.user.is_authenticated:
        user = request.user
        watched_by = True if user.watchlist.filter(title=listing.title).exists() else False
        print(watched_by)
        context = {
            "listing" : listing,
            "watchedBy" : watched_by
        }
    else:
        context = {
            "listing" : listing
        }
    return render(request,"auctions/listing.html",context)

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

