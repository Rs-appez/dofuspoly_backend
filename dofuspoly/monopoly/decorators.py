from .exceptions import GameException

from functools import wraps


def player_turn_required(func):
    @wraps(func)
    def wrapper(self, game, *args, **kwargs):
        from .models import Player

        if not isinstance(self, Player):
            raise Exception("Decorator can only be used on player instance methods")
        if game.current_player != self:
            raise GameException("It's not your turn")
        return func(self, game, * args, **kwargs)

    return wrapper


def is_player_in_game(func):
    from .models import Player

    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        game = self.get_object()
        player = Player.objects.get(user=request.user)
        if not game:
            raise GameException("Game not found")
        if not player:
            raise GameException("Player not found")
        if player not in game.players.all():
            raise GameException("You are not a player in this game")

        return func(self, request, game=game, *args, **kwargs)

    return wrapper
