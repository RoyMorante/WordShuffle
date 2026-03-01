from django.contrib import admin
from .models import RaffleSetting, RaffleEntry, RaffleWinner

admin.site.register(RaffleSetting)
admin.site.register(RaffleEntry)
admin.site.register(RaffleWinner)