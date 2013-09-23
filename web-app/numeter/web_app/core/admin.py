from django.contrib import admin
from core.models import Storage, Host, Plugin, Data_Source, User, Group


admin.site.register(User)
admin.site.register(Group)
admin.site.register(Storage)
admin.site.register(Host)
admin.site.register(Plugin)
admin.site.register(Data_Source)
