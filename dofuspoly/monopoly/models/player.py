import uuid

from django.db import models

from ..decorators import player_turn_required
from ..exceptions import GameException
from .space import Space, OwnedSpace


class Player(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    money = models.IntegerField()
    position = models.IntegerField()
    has_rolled = models.BooleanField(default=True)
    nb_double_rolls = models.IntegerField(default=0)
    in_jail = models.BooleanField(default=False)
    jail_turns = models.IntegerField(default=0)
    cards = models.ManyToManyField("Card", blank=True)
    image = models.CharField(max_length=255, default="default.png")
    game = models.ForeignKey("Game", on_delete=models.CASCADE, related_name="players")

    def __str__(self):
        return self.user.username

    def update_money(self, amount: int):
        self.money += amount
        self.save()

        if self.money < 0:
            raise GameException("Player is bankrupt")

    def start_gain(self):
        self.update_money(self.game.start_gain_amount)

    def start_turn(self):
        self.has_rolled = False
        self.nb_double_rolls = 0
        self.save()

    @player_turn_required
    def end_turn(self):
        if not self.has_rolled:
            raise GameException("You must roll before ending your turn")
        if self.money < 0:
            raise GameException("You are bankrupt and cannot end your turn")

        self.game.end_turn()

    @player_turn_required
    def can_player_roll(self) -> bool:
        if self.has_rolled:
            raise GameException("You have already rolled this turn")

        return True

    def move(self, dice_values: [int, int]):
        self.has_rolled = True
        if self.in_jail:
            if self.__handle_jail_turn(dice_values):
                return

        if dice_values[0] == dice_values[1]:
            self.nb_double_rolls += 1
            if self.nb_double_rolls >= 3:
                self.__go_to_jail()
                return
            else:
                self.has_rolled = False

        self.position += sum(dice_values)
        if self.position >= 40:
            self.position = self.position % 40
            self.start_gain()
        self.save()

    def __handle_jail_turn(self, dice_values: [int, int]):
        """Handles the player's turn when they are in jail.
        Returns True if the player remains in jail, False otherwise.
        """
        if dice_values[0] == dice_values[1]:
            self.__leave_jail()
            return False
        else:
            self.jail_turns += 1
            if self.jail_turns >= 3:
                self.pay_jail_fee()
                self.__leave_jail()
                return False
        return True

    def __leave_jail(self):
        self.in_jail = False
        self.jail_turns = 0
        self.save()

    @player_turn_required
    def pay_jail_fee(self):
        if not self.in_jail:
            raise GameException("You are not in jail")

        if self.money < self.game.jail_fee_amount:
            raise GameException("You don't have enough money to pay the jail fee")

        self.update_money(-self.game.jail_fee_amount)

    def __go_to_jail(self):
        jail_space = self.game.board.spaces.get(type__type="Jail")
        self.position = jail_space.position
        self.in_jail = True
        self.save()

    @player_turn_required
    def trigger_space_effect(self):
        space = self.game.board.spaces.get(position=self.position)
        if (
            owner := self.game.players.filter(
                owned_spaces__space__position=self.position,
            )
            .exclude(id=self.id)
            .first()
        ):
            rent = owner.owned_spaces.get(
                space__position=self.position
            ).calculate_rent()
            self.update_money(-rent)
            owner.update_money(rent)
            owner.save()

        match space.type.type:
            case "Tax":
                self.update_money(-space.tax_amount)
            case "Go to Jail":
                self.__go_to_jail()
                self.end_turn()
            case "Chance":
                pass  # To be implemented
            case "Community Chest":
                pass  # To be implemented
            case "Free Parking":
                pass  # No effect

        self.save()

    @player_turn_required
    def buy_space(self, space: Space):
        if self.game.players.filter(owned_spaces__space=space).first():
            raise GameException("This space is already owned")

        if self.money < space.price:
            raise GameException("You don't have enough money to buy this space")

        if not self.has_rolled and self.nb_double_rolls == 0:
            raise GameException("You must roll before buying a space")

        owned_space = OwnedSpace.objects.create(space=space)
        self.owned_spaces.add(owned_space)
        self.update_money(-space.price)
        self.save()
