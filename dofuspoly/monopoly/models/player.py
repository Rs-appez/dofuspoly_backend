import uuid

from django.db import models

from ..decorators import player_turn_required
from ..exceptions import GameException
from .game import Game
from .space import Space, OwnedSpace


class Player(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    money = models.IntegerField()
    position = models.IntegerField()
    has_rolled = models.BooleanField(default=True)
    in_jail = models.BooleanField(default=False)
    jail_turns = models.IntegerField(default=0)
    cards = models.ManyToManyField("Card", blank=True)
    owned_spaces = models.ManyToManyField("OwnedSpace", blank=True)
    image = models.CharField(max_length=255, default="default.png")

    def __str__(self):
        return self.user.username

    def get_current_game(self):
        return Game.objects.filter(players=self, finished=False).first()

    def update_money(self, amount: int):
        self.money += amount
        self.save()

        if self.money < 0:
            raise GameException("Player is bankrupt")


    def start_turn(self):
        self.has_rolled = False
        self.save()

    @player_turn_required
    def end_turn(self, game: Game):
        if not self.has_rolled:
            raise GameException("You must roll before ending your turn")
        if self.money < 0:
            raise GameException("You are bankrupt and cannot end your turn")

        game.end_turn()

    @player_turn_required
    def can_player_roll(self, game: Game) -> bool:
        if self.has_rolled:
            raise GameException("You have already rolled this turn")

        return True

    def move(self, dice_values: [int, int]):
        if self.in_jail and dice_values[0] != dice_values[1]:
            return

        self.position += sum(dice_values)
        self.position = self.position % 40
        self.save()

    @player_turn_required
    def trigger_space_effect(self, game: Game):
        space = game.board.spaces.get(position=self.position)
        if owner := game.players.filter(
            owned_spaces__space__position=self.position
        ).first():
            rent = owner.owned_spaces.get(space__position=self.position).calculate_rent()
            self.update_money(-rent)
            owner.update_money(rent)
            owner.save()

        elif space.type.type == "Tax":
            self.money -= space.price
        elif space.type.type == "Go to Jail":
            jail_space = game.board.spaces.get(type__type="Jail")
            self.position = jail_space.position
            self.in_jail = True
            self.jail_turns = 0
        elif space.type.type == "Chance":
            pass  # To be implemented
        elif space.type.type == "Community Chest":
            pass  # To be implemented
        elif space.type.type == "Free Parking":
            pass  # No effect
        elif space.type.type == "Start":
            self.update_money(200)

        self.save()

    @player_turn_required
    def buy_space(self, game: Game, space: Space):
        if game.players.filter(owned_spaces__space=space).first():
            raise GameException("This space is already owned")

        if self.money < space.price:
            raise GameException("You don't have enough money to buy this space")

        owned_space = OwnedSpace.objects.create(space=space)
        self.owned_spaces.add(owned_space)
        self.update_money(-space.price)
        self.save()
