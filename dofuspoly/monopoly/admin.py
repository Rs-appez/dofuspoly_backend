from django.contrib import admin

from .models import Game, Player, Board, Space, Color, Rent, SpaceType, Card, CardType

admin.site.register(Game)
admin.site.register(Player)
admin.site.register(Board)
admin.site.register(Space)
admin.site.register(Color)
admin.site.register(Rent)
admin.site.register(SpaceType)
admin.site.register(Card)
admin.site.register(CardType)

