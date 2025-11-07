from rest_framework import serializers
from .models import Board, Color, Space, Game, Rent, SpaceType, Card, CardType, Player
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


class SpaceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpaceType
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


class SpaceSerializer(serializers.ModelSerializer):
    color = ColorSerializer()
    type = SpaceTypeSerializer()

    class Meta:
        model = Space
        fields = ["name", "price", "type", "color", "position"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["type"] = representation["type"]["type"]
        if representation["color"]:
            representation["color"] = representation["color"]["name"]
        return representation


class BoardSerializer(serializers.ModelSerializer):
    spaces = SpaceSerializer(many=True)

    class Meta:
        model = Board
        fields = ["spaces"]


class GameSerializer(serializers.ModelSerializer):
    board = BoardSerializer()
    players = PlayerSerializer(many=True)
    current_player = PlayerSerializer()

    class Meta:
        model = Game
        fields = "__all__"
