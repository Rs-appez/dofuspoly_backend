from django.db import models

class Game(models.Model):
    board = models.ForeignKey('Board', on_delete=models.CASCADE)
    players = models.ManyToManyField('Player')
    current_player = models.ForeignKey('Player', null=True, blank=True)
    turn = models.IntegerField(default=0)
    finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.created_at

class Board(models.Model):
    cases = models.ManyToManyField('Case')


class Color(models.Model):
    name = models.CharField(max_length=255)
    price_house = models.IntegerField()

    def __str__(self):
        return self.name
    

class Case(models.Model):
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    owner = models.ForeignKey('Player', null=True, blank=True)
    type = models.ForeignKey('CaseType', on_delete=models.CASCADE)
    color = models.ForeignKey('Color', null=True, blank=True)
    houses = models.IntegerField(default=0)
    rent = models.ForeignKey('Rent', null=True, blank=True)

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
    type = models.ForeignKey('CardType', on_delete=models.CASCADE)
    value = models.IntegerField()

    def __str__(self):
        return self.name
    
class CardType(models.Model):
    type = models.CharField(max_length=255)

    def __str__(self):
        return self.type

class Player(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    money = models.IntegerField()
    position = models.IntegerField()
    in_jail = models.BooleanField(default=False)
    jail_turns = models.IntegerField(default=0)
    cards = models.ManyToManyField('Card')    

    def __str__(self):
        return self.name
