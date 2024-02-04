from django.contrib import admin
from .models import User, Type, Listing, Comment, Bid
# Register your models here.

admin.site.register(User)
admin.site.register(Type)
admin.site.register(Listing)
admin.site.register(Comment)
admin.site.register(Bid)