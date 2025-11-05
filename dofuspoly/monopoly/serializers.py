from rest_framework import serializers
from .models import Board, Color, Case, Game, Rent, CaseType, Card, CardType, Player
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username"]


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ["name"]


class RentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rent
        fields = "__all__"


class CaseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseType
        fields = ["type"]


class CardTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardType
        fields = ["type"]


class CardSerializer(serializers.ModelSerializer):
    type = CardTypeSerializer()

    class Meta:
        model = Card
        fields = ["name", "description", "type", "value"]


class PlayerSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True)
    username = UserSerializer(source="user")

    class Meta:
        model = Player
        fields = [
            "username",
            "money",
            "position",
            "in_jail",
            "jail_turns",
            "cards",
            "image",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["username"] = representation["username"]["username"]

        return representation


class CaseSerializer(serializers.ModelSerializer):
    color = ColorSerializer()
    type = CaseTypeSerializer()

    class Meta:
        model = Case
        fields = ["name", "price", "type", "color"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["type"] = representation["type"]["type"]
        if representation["color"]:
            representation["color"] = representation["color"]["name"]
        return representation


class BoardSerializer(serializers.ModelSerializer):
    cases = CaseSerializer(many=True)

    class Meta:
        model = Board
        fields = ["cases"]


class GameSerializer(serializers.ModelSerializer):
    board = BoardSerializer()
    players = PlayerSerializer(many=True)
    current_player = PlayerSerializer()

    class Meta:
        model = Game
        fields = "__all__"
