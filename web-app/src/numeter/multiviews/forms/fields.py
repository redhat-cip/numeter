from datetime import date
from django.forms import widgets

class Super_SelectMultiple(widgets.MultiWidget):
    def __init__(self, Search_in, choices=None, attrs=None):
        # create choices for days, months, years
        # example below, the rest snipped for brevity.
        _widgets = (
            widgets.TextInput(attrs=attrs), # Search bar
            widgets.SelectMultiple(attrs=attrs), # search result
            widgets.SelectMultiple(attrs=attrs),
        )
        super(Super_SelectMultiple, self).__init__(_widgets, attrs)

    def decompress(self, value):
        return value
