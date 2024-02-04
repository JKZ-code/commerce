from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Type, Listing, Comment, Bid


def index(request):
    activeListings = Listing.objects.filter(isActive=True)
    allTypes = Type.objects.all()
    return render(request, "auctions/index.html", {
        "listings": activeListings,
        "types": allTypes
    })

def listing(request, id):
    listingData = Listing.objects.get(pk=id)
    isListinginWatchinglist = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    isOwner = request.user.username == listingData.owner.username
    return render(request, "auctions/listing.html", {
        "listing":listingData,
        "isListinginWatchinglist":isListinginWatchinglist,
        "allComments":allComments,
        "isOwner": isOwner
    })

def closeAuction(request, id):
    listingData = Listing.objects.get(pk=id)
    listingData.isActive = False
    listingData.save()
    isOwner = request.user.username == listingData.owner.username
    isListinginWatchinglist = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)

    return render(request, "auctions/listing.html", {
        "listing":listingData,
        "isListinginWatchinglist":isListinginWatchinglist,
        "allComments":allComments,
        "isOwner": isOwner,
        "update": True,
        "message": "Your auction is closed."
    })


def addComment(request, id):
    currentUser = request.user
    listingData = Listing.objects.get(pk=id)
    message = request.POST["newComment"]
    newComment = Comment(
        author=currentUser,
        listing=listingData,
        message=message
    )
    newComment.save()
    return HttpResponseRedirect(reverse("listing", args=(id,)))


def addBid(request, id):
    newBid = request.POST["newBid"]
    listingData = Listing.objects.get(pk=id)
    isListinginWatchinglist = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    isOwner = request.user.username == listingData.owner.username
    if int(newBid) > listingData.price.bid:
        updateBid = Bid(user=request.user, bid=int(newBid))
        updateBid.save()
        listingData.price = updateBid
        listingData.save()
        return render(request, "auctions/listing.html", {
            "listing": listingData,
            "message": "Successfully Bid!",
            "update" : True,
            "isListinginWatchinglist":isListinginWatchinglist,
            "allComments":allComments,
            "isOwner": isOwner 
        })
    else:
        return render(request, "auctions/listing.html", {
            "listing": listingData,
            "message": "Bid Failed!",
            "update" : False,
            "isListinginWatchinglist":isListinginWatchinglist,
            "allComments":allComments,
            "isOwner": isOwner 
        })



def displayWatchlist(request):
    currentUser = request.user
    listings = currentUser.listingWatchlist.all()
    return render(request, "auctions/watchlist.html", {
        "listings":listings
    })


def removeWatchlist(request, id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.remove(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id,)))


def addWatchlist(request, id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.add(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id,)))


def displayType(request):
    if request.method == "POST":
        typeFromForm = request.POST["type"]
        type = Type.objects.get(typeName=typeFromForm)
        activeListings = Listing.objects.filter(isActive=True, type=type)
        allTypes = Type.objects.all()
        return render(request, "auctions/index.html", {
            "listings": activeListings,
            "types": allTypes
        })

def createListing(request):
    if request.method == "GET":
        allTypes = Type.objects.all()
        return render(request, "auctions/create.html", {
            "types":allTypes
        })
    else:
        name = request.POST["name"]
        description = request.POST["description"]
        imageurl = request.POST["imageurl"]
        price = request.POST["price"]
        type = request.POST["type"]

        currentUser = request.user
        typeData = Type.objects.get(typeName=type)

        bid = Bid(bid=int(price), user=currentUser)
        bid.save()

        newListing = Listing(
            name = name,
            description = description,
            imageUrl = imageurl,
            price = bid,
            type = typeData,
            owner = currentUser
        )
        newListing.save()
        return HttpResponseRedirect(reverse(index))



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
