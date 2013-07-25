from django.contrib import admin
from multiviews.models import Plugin, Multiview, View, Event, Data_Source

admin.site.register(Plugin)
admin.site.register(Multiview)
admin.site.register(Data_Source)
admin.site.register(View)
admin.site.register(Event)
