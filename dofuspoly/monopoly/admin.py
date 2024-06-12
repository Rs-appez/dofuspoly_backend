from django.contrib import admin

from .models import Game, Player, Board, Case, Color, Rent, CaseType, Card, CardType

admin.site.register(Game)
admin.site.register(Player)
admin.site.register(Board)
admin.site.register(Case)
admin.site.register(Color)
admin.site.register(Rent)
admin.site.register(CaseType)
admin.site.register(Card)
admin.site.register(CardType)

