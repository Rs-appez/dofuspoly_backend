from django.db import models
from ..exceptions import GameException


class Space(models.Model):
    name = models.CharField(max_length=255)
    position = models.IntegerField()
    price = models.IntegerField()
    type = models.ForeignKey("SpaceType", on_delete=models.PROTECT)
    color = models.ForeignKey("Color", null=True, blank=True, on_delete=models.PROTECT)
    rent = models.ForeignKey("Rent", null=True, blank=True, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name

    def is_property(self) -> bool:
        return self.type.is_property()


class SpaceType(models.Model):
    type = models.CharField(max_length=255)

    def __str__(self):
        return self.type

    def is_property(self) -> bool:
        return self.type in ["Street", "Railroad", "Utility"]


class OwnedSpace(models.Model):
    space = models.ForeignKey("Space", on_delete=models.CASCADE)
    player = models.ForeignKey(
        "Player", on_delete=models.CASCADE, related_name="owned_spaces"
    )
    is_mortgaged = models.BooleanField(default=False)
    houses = models.IntegerField(default=0)
    has_hotel = models.BooleanField(default=False)

    def calculate_rent(self) -> int:
        if self.is_mortgaged:
            return 0

        match self.space.type.type:
            case "Railroad":
                return self.__railroad_rent()
            case "Utility":
                game = self.player.game
                dice_total = game.dice1Value + game.dice2Value
                return self.__utility_rent(dice_total)
            case "Street":
                return self.__street_rent()
            case _:
                raise GameException("This space type has no rent")

    def __railroad_rent(self) -> int:
        nb_railroads_owned = self.player.owned_spaces.filter(
            space__type__type="Railroad"
        ).count()
        match nb_railroads_owned:
            case 1:
                return 25
            case 2:
                return 50
            case 3:
                return 100
            case 4:
                return 200
            case _:
                raise GameException("Invalid number of railroads owned")

    def __utility_rent(self, dice_total: int) -> int:
        nb_utilities_owned = self.player.owned_spaces.filter(
            space__type__type="Utility"
        ).count()

        if nb_utilities_owned == 1:
            return dice_total * 4
        elif nb_utilities_owned == 2:
            return dice_total * 10
        else:
            return 0

    def __street_rent(self) -> int:
        rent = self.space.rent.rent

        if self.has_hotel:
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

        nb_color_owned = self.player.owned_spaces.filter(
            space__color=self.space.color
        ).count()

        if nb_color_owned == self.space.color.nb_spaces and self.houses == 0:
            rent *= 2

        return rent

    def calculate_mortgage_value(self) -> int:
        if self.is_mortgaged:
            raise GameException("Space is already mortgaged")

        match self.space.type.type:
            case "Railroad":
                return 100
            case "Utility":
                return self.space.price // 2
            case "Street":
                return self.space.rent.mortage
            case _:
                raise GameException("This space type cannot be mortgaged")


class Rent(models.Model):
    price_house = models.IntegerField()
    mortage = models.IntegerField()
    rent = models.IntegerField()
    rent_1_house = models.IntegerField()
    rent_2_houses = models.IntegerField()
    rent_3_houses = models.IntegerField()
    rent_4_houses = models.IntegerField()
    rent_hotel = models.IntegerField()


class Color(models.Model):
    name = models.CharField(max_length=255)
    nb_spaces = models.IntegerField(default=3)

    def __str__(self):
        return self.name
