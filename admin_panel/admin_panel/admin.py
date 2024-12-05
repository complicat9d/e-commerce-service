from django.contrib import admin
from .models import User, Product, Cart, Category, FAQ

admin.site.register(User)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Category)
admin.site.register(FAQ)

admin.site.site_header = "Admin panel"
admin.site.site_title = "Admin panel"
