from django.db import models


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
    is_mortgaged = models.BooleanField(default=False)
    houses = models.IntegerField(default=0)
    has_hotel = models.BooleanField(default=False)

    def calculate_rent(self) -> int:
        if self.is_mortgaged:
            return 0

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

        return rent


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

    def __str__(self):
        return self.name
