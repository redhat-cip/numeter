from django.contrib import admin
from core.models import Host, Storage, User, Group

admin.site.register(User)
admin.site.register(Group)
admin.site.register(Host)
admin.site.register(Storage)
