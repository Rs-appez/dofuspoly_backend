import random
import uuid

from django.db import models

from .exceptions import GameException
from .decorators import player_turn_required


class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    board = models.ForeignKey("Board", on_delete=models.CASCADE)
    players = models.ManyToManyField("Player")
    current_player = models.ForeignKey(
        "Player",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="current_player",
    )
    turn = models.IntegerField(default=0)
    dice1Value = models.IntegerField(default=6)
    dice2Value = models.IntegerField(default=6)
    finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    def roll_dice(self):
        if not self.current_player:
            raise GameException("No current player set")

        if self.current_player.can_player_roll(self):
            self.current_player.has_rolled = True
            self.dice1Value = random.randint(1, 6)
            self.dice2Value = random.randint(1, 6)

            self.current_player.move((self.dice1Value, self.dice2Value))

            self.save()

    def end_turn(self):
        players = list(self.players.all())
        current_index = players.index(self.current_player)
        next_index = (current_index + 1) % len(players)
        self.current_player = players[next_index]
        self.current_player.allow_roll()
        self.turn += 1
        self.save()


class Board(models.Model):
    spaces = models.ManyToManyField("Space")

    def make_board(self):
        self.spaces.clear()
        for case in Space.objects.all():
            self.spaces.add(case)

        self.save()


class Color(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Space(models.Model):
    name = models.CharField(max_length=255)
    position = models.IntegerField()
    price = models.IntegerField()
    type = models.ForeignKey("SpaceType", on_delete=models.PROTECT)
    color = models.ForeignKey("Color", null=True, blank=True, on_delete=models.PROTECT)
    rent = models.ForeignKey("Rent", null=True, blank=True, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name


class Rent(models.Model):
    price_house = models.IntegerField()
    mortage = models.IntegerField()
    rent = models.IntegerField()
    rent_1_house = models.IntegerField()
    rent_2_houses = models.IntegerField()
    rent_3_houses = models.IntegerField()
    rent_4_houses = models.IntegerField()
    rent_hotel = models.IntegerField()


class SpaceType(models.Model):
    type = models.CharField(max_length=255)

    def __str__(self):
        return self.type


class Card(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    type = models.ForeignKey("CardType", on_delete=models.CASCADE)

    image = models.ImageField(upload_to="statics/cards/")
    image_back = models.ImageField(upload_to="statics/cards/", null=True, blank=True)

    def __str__(self):
        return self.name


class CardType(models.Model):
    type = models.CharField(max_length=255)

    def __str__(self):
        return self.type


class Player(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    money = models.IntegerField()
    position = models.IntegerField()
    has_rolled = models.BooleanField(default=True)
    in_jail = models.BooleanField(default=False)
    jail_turns = models.IntegerField(default=0)
    cards = models.ManyToManyField("Card", blank=True)
    ownedSpace = models.ManyToManyField("OwnedSpace", blank=True)
    image = models.CharField(max_length=255, default="default.png")

    def __str__(self):
        return self.user.username

    def get_current_game(self):
        return Game.objects.filter(players=self, finished=False).first()

    def allow_roll(self):
        self.has_rolled = False
        self.save()

    @player_turn_required
    def end_turn(self, game: Game):
        if not self.has_rolled:
            raise GameException("You must roll before ending your turn")
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
    def buy_space(self, game: Game, space: Space):
        if self.money < space.price:
            raise GameException("You don't have enough money to buy this space")

        if game.players.filter(ownedSpace__space=space).first():
            raise GameException("This space is already owned")

        owned_space = OwnedSpace.objects.create(space=space)
        self.ownedSpace.add(owned_space)
        self.money -= space.price
        self.save()


class OwnedSpace(models.Model):
    space = models.ForeignKey("Space", on_delete=models.CASCADE)
    mortgaged = models.BooleanField(default=False)
    houses = models.IntegerField(default=0)
    hotel = models.BooleanField(default=False)

    def calculate_rent(self) -> int:
        if self.mortgaged:
            return 0

        rent = self.space.rent.rent

        if self.hotel:
            rent = self.space.rent.rent_hotel
        else:
            if self.houses == 1:
                rent = self.space.rent.rent_1_house
            elif self.houses == 2:
                rent = self.space.rent.rent_2_houses
            elif self.houses == 3:
                rent = self.space.rent.rent_3_houses
            elif self.houses == 4:
                rent = self.space.rent.rent_4_houses

        return rent
