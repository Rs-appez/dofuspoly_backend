from django.db import models
import random
import uuid
from ..exceptions import GameException
from .space import Space


class Board(models.Model):
    spaces = models.ManyToManyField("Space")

    def make_board(self):
        self.spaces.clear()
        for case in Space.objects.all():
            self.spaces.add(case)

        self.save()


class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    board = models.ForeignKey("Board", on_delete=models.CASCADE)
    current_player = models.ForeignKey(
        "Player",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="current_player",
    )
    turn = models.IntegerField(default=0)
    start_gain_amount = models.IntegerField(default=200)
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

    def end_turn(self):
        players = list(self.players.all())
        current_index = players.index(self.current_player)
        next_index = (current_index + 1) % len(players)
        self.current_player = players[next_index]
        self.current_player.start_turn()
        self.turn += 1
        self.save()
