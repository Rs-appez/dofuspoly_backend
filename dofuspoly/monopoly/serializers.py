from rest_framework import serializers
from .models import (
    Board,
    Color,
    Space,
    Game,
    Rent,
    SpaceType,
    Card,
    CardType,
    Player,
    OwnedSpace,
)
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


class OwnedSpaceSerializer(serializers.ModelSerializer):
    space = serializers.StringRelatedField()

    class Meta:
        model = OwnedSpace
        fields = ["space", "houses", "has_hotel", "is_mortgaged"]


class PlayerSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True)
    username = UserSerializer(source="user")
    owned_spaces = OwnedSpaceSerializer(many=True)

    class Meta:
        model = Player
        fields = [
            "username",
            "money",
            "position",
            "has_rolled",
            "in_jail",
            "jail_turns",
            "cards",
            "owned_spaces",
            "image",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["username"] = representation["username"]["username"]

        return representation


class SpaceSerializer(serializers.ModelSerializer):
    color = ColorSerializer()
    type = SpaceTypeSerializer()
    can_be_bought = serializers.SerializerMethodField()

    class Meta:
        model = Space
        fields = ["name", "price", "type", "color", "position", "can_be_bought"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["type"] = representation["type"]["type"]
        if representation["color"]:
            representation["color"] = representation["color"]["name"]
        return representation

    def get_can_be_bought(self, obj):
        if obj.is_property():
            return True
        return False


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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["current_player"] = representation["current_player"]["username"]
        return representation
