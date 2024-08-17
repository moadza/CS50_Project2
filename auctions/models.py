from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass
    watchlist = models.ManyToManyField('Listing', blank=True, related_name="watched_by")

    def __str__(self):
        return f"{self.username} {self.watchlist}"


""" class Categoryus(models.Model):
    category = models.CharField(max_length=64)
    
    def __str__(self):
        return f"{self.category}"  """

class Listing(models.Model):
    CATEGORY_CHOICES = [
    ('ELE', 'Electronics'),
    ('FAS', 'Fashion'),
    ('HOM', 'Home & Garden'),
    ('SPO', 'Sports & Outdoors'),
    ('AUT', 'Automotive'),
    ('COL', 'Collectibles & Art'),
    ('TOY', 'Toys & Hobbies'),
    ('BOK', 'Books & Media'),
    ('REA', 'Real Estate'),
    ('OTH', 'Other')
    ] 

    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=15, decimal_places=2)
    image = models.ImageField(upload_to='auctions/media/listing_images', blank=True, null=True)
    category = models.CharField(max_length=3, choices=CATEGORY_CHOICES, blank=True, null=True)
    active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")

    def __str__(self):
        return f"{self.title} : {self.starting_bid} owner {self.owner}"

class Bid(models.Model):
    price = models.IntegerField()
    date = models.DateField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    Listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")

class Comment(models.Model):
    content = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    Listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")

