from rest_framework import serializers
from .models import Board, Color, Case, Game, Rent, CaseType, Card, CardType, Player
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['name']

class RentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rent
        fields = '__all__'

class CaseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseType
        fields = ['type']

class CardTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardType
        fields = ['type']

class CardSerializer(serializers.ModelSerializer):
    type = CardTypeSerializer()

    class Meta:
        model = Card
        fields = ['name', 'description', 'type', 'value']

class PlayerSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True)
    user = UserSerializer()

    class Meta:
        model = Player
        fields = ['user', 'money', 'position', 'in_jail', 'jail_turns', 'cards', 'image']

class CaseSerializer(serializers.ModelSerializer):
    type = CaseTypeSerializer()
    color = ColorSerializer()
    rent = RentSerializer()

    class Meta:
        model = Case
        fields = ['name', 'price', 'type', 'color', 'rent']

class BoardSerializer(serializers.ModelSerializer):
    cases = CaseSerializer(many=True)

    class Meta:
        model = Board
        fields = ['cases']

class GameSerializer(serializers.ModelSerializer):
    board = BoardSerializer()
    players = PlayerSerializer(many=True)

    class Meta:
        model = Game
        fields = '__all__'

