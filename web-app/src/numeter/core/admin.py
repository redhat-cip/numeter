from django.contrib import admin
from core.models import Host, Storage, User, GraphLib

admin.site.register(User)
admin.site.register(Host)
admin.site.register(Storage)
admin.site.register(GraphLib)
