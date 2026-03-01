from django.contrib import admin
from .models import Criteria, Vote, VoteScore

admin.site.register(Criteria)
admin.site.register(Vote)
admin.site.register(VoteScore)