from rest_framework import serializers
from .models import Board, Color, Case, Game, Rent, CaseType, Card, CardType, Player

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['name', 'price_house']

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

    class Meta:
        model = Player
        fields = ['user', 'money', 'position', 'in_jail', 'jail_turns', 'cards']

class CaseSerializer(serializers.ModelSerializer):
    owner = PlayerSerializer()
    type = CaseTypeSerializer()
    color = ColorSerializer()
    rent = RentSerializer()

    class Meta:
        model = Case
        fields = ['name', 'price', 'owner', 'type', 'color', 'houses', 'rent']

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