import random
import uuid

from django.db import models

from .exceptions import GameException


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

        if self.current_player.can_player_roll():
            self.current_player.has_rolled = True
            self.dice1Value = random.randint(1, 6)
            self.dice2Value = random.randint(1, 6)

            self.current_player.move((self.dice1Value, self.dice2Value))

            self.save()


class Board(models.Model):
    cases = models.ManyToManyField("Case")

    def make_board(self):
        self.cases.clear()
        for case in Case.objects.all():
            self.cases.add(case)

        self.save()


class Color(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Case(models.Model):
    name = models.CharField(max_length=255)
    position = models.IntegerField()
    price = models.IntegerField()
    type = models.ForeignKey("CaseType", on_delete=models.PROTECT)
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


class CaseType(models.Model):
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
    ownedCase = models.ManyToManyField("OwnedCase", blank=True)
    image = models.CharField(max_length=255, default="default.png")

    def __str__(self):
        return self.user.username

    def can_player_roll(self) -> bool:
        if self.has_rolled:
            raise GameException("You have already rolled this turn")

        return True

    def move(self, dice_values: [int, int]):
        if self.in_jail and dice_values[0] != dice_values[1]:
            return

        self.position += sum(dice_values)
        self.position = self.position % 40
        self.save()

    def get_current_game(self):
        return Game.objects.filter(players=self, finished=False).first()


class OwnedCase(models.Model):
    case = models.ForeignKey("Case", on_delete=models.CASCADE)
    mortgaged = models.BooleanField(default=False)
    houses = models.IntegerField(default=0)
    hotel = models.BooleanField(default=False)
