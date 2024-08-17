# game.py
from __future__ import annotations

import bisect
import enum
import random
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

import numpy as np
from pydantic import BaseModel, field_validator, computed_field, Field


class CardType(str, enum.Enum):
    TRUMP = "TRUMP"
    FOOL = "FOOL"
    SIMPLE_CARD = "SIMPLE_CARD"


class Card(BaseModel, ABC):
    is_face_down: bool = False
    is_playable: bool = False
    card_type: CardType

    @computed_field
    def path(self) -> str:
        if self.is_face_down:
            return BACK_CARD_PATH
        return self._path

    @computed_field
    @abstractmethod
    def _path(self) -> str:
        raise NotImplementedError

    @computed_field
    @abstractmethod
    def point(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def is_oudler(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __lt__(self, other: Card) -> bool:
        pass


BACK_CARD_PATH = f"/static/images/cardback.jpg"
CARD_PLACEHOLDER_PATH = f"/static/images/card_placeholder.png"


class TrumpCard(Card):
    value: int
    card_type: CardType = CardType.TRUMP

    @field_validator('value')
    @classmethod
    def val(cls, v: int) -> int:
        assert 1 <= v <= 21
        return v

    @computed_field
    def _path(self) -> str:
        if self.value < 10:
            val = f"0{self.value}"
        else:
            val = f"{self.value}"
        return f"/static/images/trumps/TN-{val}.jpg"

    @computed_field
    def is_oudler(self) -> bool:
        return self.value in [1, 21]

    @computed_field
    def point(self) -> int:
        if self.is_oudler:
            return 5
        else:
            return 1

    def __lt__(self, other: Card) -> bool:
        if isinstance(other, TrumpCard):
            return self.value < other.value
        return False  # Trump cards are always greater than any non-Trump card


class Fool(Card):
    card_type: CardType = CardType.FOOL

    @computed_field
    def _path(self) -> str:
        return f"/static/images/trumps/TN-00.jpg"

    @computed_field
    def is_oudler(self) -> bool:
        return True

    @computed_field
    def point(self) -> int:
        return 5

    def __lt__(self, other: Card) -> bool:
        if isinstance(other, Fool):
            return False
        elif isinstance(other, TrumpCard):
            return True  # Fool is less than any Trump card
        return False  # Fool is greater than any non-Trump card


class Suit(str, enum.Enum):
    SPADES = "spades"
    HEARTS = "hearts"
    DIAMONDS = "diamonds"
    CLUBS = "clubs"

    @classmethod
    def value_list(cls) -> List[str]:
        return list(map(lambda c: c.value, cls))


class SimpleCard(Card):
    value: int
    suit: Suit
    card_type: CardType = CardType.SIMPLE_CARD

    @computed_field
    def _path(self) -> str:
        extension = "png"
        if self.value <= 10:
            val = self.value if self.value > 1 else "ace"
        elif self.value == 11:
            val = "jack"
        elif self.value == 12:
            val = "knight"
            extension = "jpeg"
        elif self.value == 13:
            val = "queen"
        elif self.value == 14:
            val = "king"
        else:
            raise ValueError(self.value)
        return f"/static/images/{val}_of_{self.suit.value}.{extension}"

    @computed_field
    def is_oudler(self) -> bool:
        return False

    @computed_field
    def point(self) -> int:
        return max(1, self.value - 9)

    def __lt__(self, other: Card) -> bool:
        if isinstance(other, SimpleCard):
            if self.suit == other.suit:
                return self.value < other.value
            # Define suit order: Spades < Hearts < Diamonds < Clubs
            suit_order = {
                Suit.SPADES: 1,
                Suit.HEARTS: 2,
                Suit.DIAMONDS: 3,
                Suit.CLUBS: 4
            }
            return suit_order[self.suit] < suit_order[other.suit]
        elif isinstance(other, (Fool, TrumpCard)):
            return True  # Any SimpleCard is less than the Fool or Trump
        else:
            raise ValueError()


class Deck(BaseModel):
    cards: List[Card] = Field(default_factory=Fool)

    def model_post_init(self, __context):
        self.cards = [Fool()]
        for t in range(1, 22):
            self.cards.append(TrumpCard(value=t))
        for suit in Suit:
            for value in range(1, 15):
                self.cards.append(SimpleCard(value=value, suit=suit))

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def deal(self, n: int) -> List[Card]:
        return [self.cards.pop() for _ in range(n)]


class CardStack(BaseModel):
    cards: List[Card]

    def model_post_init(self, __context):
        for card in self.cards[:-1]:
            card.is_face_down = True

    def set_all_cards_not_playable(self) -> None:
        for card in self.cards:
            card.is_playable = False

    def get_facecard(self) -> Card:
        return self.cards[-1]


class CardHand(BaseModel):
    cards: List[Card]

    def model_post_init(self, __context):
        self.cards = sorted(self.cards)

    def set_all_cards_playability(self, playable: bool) -> None:
        for card in self.cards:
            card.is_playable = playable


class Player(BaseModel):
    username: str
    hand: CardHand
    session_id: str
    cards_on_table: List[CardStack]
    sorted_available_cards: Dict[Suit | CardType, List[Card]] = {}
    backcard: str = BACK_CARD_PATH
    card_placeholder: str = CARD_PLACEHOLDER_PATH
    game_score: int = 0
    game_n_oudler: int = 0

    @computed_field
    def n_cards(self) -> int:
        return len(self.hand.cards) + sum([len(stack.cards) for stack in self.cards_on_table])

    def on_game_reset(self) -> None:
        self.game_score = 0
        self.game_n_oudler = 0

    def model_post_init(self, __context):
        self.sort_cards()

    def sort_cards(self):
        self.sorted_available_cards = {CardType.TRUMP: [], CardType.FOOL: [], **{suit: [] for suit in Suit}}
        for card in self.hand.cards:
            self.insert_card_sorted(card=card)
        for stack in self.cards_on_table:
            self.insert_card_sorted(card=stack.get_facecard())

    def insert_card_sorted(self, card):
        if isinstance(card, SimpleCard):
            bisect.insort(self.sorted_available_cards[card.suit], card)
        else:
            bisect.insort(self.sorted_available_cards[card.card_type], card)

    def remove_card_sorted(self, card):
        if isinstance(card, SimpleCard):
            self.sorted_available_cards[card.suit].remove(card)
        else:
            self.sorted_available_cards[card.card_type].remove(card)

    def set_all_cards_not_playable(self) -> None:
        for card_stack in self.cards_on_table:
            card_stack.set_all_cards_not_playable()
        self.hand.set_all_cards_playability(playable=False)

    def set_all_cards_playable(self) -> None:
        for card_stack in self.cards_on_table:
            if len(card_stack.cards) > 0:
                card_stack.get_facecard().is_playable = True
        self.hand.set_all_cards_playability(playable=True)

    def update_stack(self, stack_index) -> tuple[Card, Card | None]:
        stack = self.cards_on_table[stack_index]
        card = stack.cards.pop()
        revealed_card = None
        if len(stack.cards) > 0:
            revealed_card = stack.cards[-1]
            self.insert_card_sorted(card=revealed_card)
        return card, revealed_card

    def compute_playable_cards(self, vs_card: Card | None) -> None:
        if vs_card is None or isinstance(vs_card, Fool):
            self.set_all_cards_playable()
            return

        trumps = self.sorted_available_cards[CardType.TRUMP]
        potential_fool = self.sorted_available_cards[CardType.FOOL]
        if isinstance(vs_card, TrumpCard):
            if len(trumps) == 0:  # can play anything
                self.set_all_cards_playable()
                return
            ind = bisect.bisect(trumps, vs_card)  # find the lowest trump bigger than vs_card
            if ind < len(trumps):  # no higher trump
                trump_subset = trumps[ind:]
            else:
                trump_subset = trumps
            for card in trump_subset + potential_fool:
                card.is_playable = True
        elif isinstance(vs_card, SimpleCard):
            suit_cards = self.sorted_available_cards[vs_card.suit]
            if len(suit_cards) > 0:  # should play a card of the suit
                for card in suit_cards + potential_fool:
                    card.is_playable = True
                return
            if len(trumps) > 0:  # should play a trump if possible
                for card in trumps + potential_fool:
                    card.is_playable = True
                return
            self.set_all_cards_playable()  # can play anything
        else:
            raise ValueError(vs_card)

    def new_game(self) -> None:
        self.cards_on_table = []
        self.game_n_oudler = 0
        self.sorted_available_cards = {}
        self.on_game_reset()


class CardGame(BaseModel):
    deck: Deck = Field(default_factory=Deck)
    players: Dict[str, Player] = {}
    player_usernames: List[str] = []
    active_player_ind: int | None = None
    active_card: Card | None = None  # card played by a user
    cards_to_reveal: list[Card] = []
    n_players: int = 0
    last_starter_player_ind: int | None = None

    def model_post_init(self, __context):
        assert len(self.players) == 0

    def shuffle_deck(self):
        self.deck.shuffle()

    def get_active_player_usn(self) -> str:
        return self.player_usernames[self.active_player_ind]

    def get_inactive_player_usn(self) -> str:
        return self.player_usernames[self.get_inactive_player_ind()]

    def get_active_player(self) -> Player:
        return self.players[self.get_active_player_usn()]

    def get_inactive_player(self) -> Player:
        return self.players[self.get_inactive_player_usn()]

    def deal_cards(self, username: str, session_id: str):
        self.shuffle_deck()
        stacks = []
        for n in range(7, 0, -1):
            stack = CardStack(cards=self.deck.deal(n=n))
            stacks.append(stack)

        card_hand = CardHand(cards=self.deck.deal(11))
        if username not in self.players:
            self.players[username] = Player(username=username, hand=card_hand,
                                            cards_on_table=stacks, session_id=session_id)
        else:
            self.players[username].hand = card_hand
            self.players[username].cards_on_table = stacks
            self.players[username].sort_cards()

        if username not in self.player_usernames:
            self.player_usernames.append(username)

        self.n_players += 1
        if self.n_players == 2:
            if self.last_starter_player_ind is None:
                self.last_starter_player_ind = np.random.choice([0, 1])
            self.last_starter_player_ind = 1 - self.last_starter_player_ind
            self.active_player_ind = self.last_starter_player_ind
            self.refresh_playable_card()
        return

    def get_inactive_player_ind(self) -> int | None:
        if self.active_player_ind is None:
            return None
        return (self.active_player_ind + 1) % 2

    def get_active_player_ind(self) -> int | None:
        return self.active_player_ind

    def _play_card(self, card: Card) -> None:
        self.get_active_player().remove_card_sorted(card=card)
        if self.active_card is None:
            self.active_card = card
            self.active_player_ind = self.get_inactive_player_ind()  # the other is to play next
        else:
            winner_id = self.compare_cards(active_player_card=card, inactive_player_card=self.active_card)
            self.active_player_ind = winner_id
            self.active_card = None
            for card in self.cards_to_reveal:
                card.is_face_down = False
                self.cards_to_reveal = []
        self.refresh_playable_card()

    def compare_cards(self, active_player_card: Card, inactive_player_card: Card) -> int:
        """ Return ID of the player who should play next and update the score """
        active_player = self.get_active_player()
        inactive_player = self.get_inactive_player()

        sum_card_points = inactive_player_card.point + active_player_card.point
        sum_n_oudlers = int(inactive_player_card.is_oudler) + int(active_player_card.is_oudler)

        fool_played = False
        if isinstance(inactive_player_card, Fool):
            fool_played = True
            winner_id = self.active_player_ind
            if inactive_player.n_cards == 0:
                active_player.game_score +=   inactive_player_card.point - 1
                active_player.game_n_oudler += 1
            else:
                inactive_player.game_score += inactive_player_card.point - 1
                inactive_player.game_n_oudler += 1
            active_player.game_score += active_player_card.point
            active_player.game_n_oudler += int(active_player_card.is_oudler)

        elif isinstance(active_player_card, Fool):
            fool_played = True
            winner_id = self.get_inactive_player_ind()
            if inactive_player.n_cards == 0:
                inactive_player.game_score += active_player_card.point - 1
                inactive_player.game_n_oudler += 1
            else:
                active_player.game_score += active_player_card.point - 1
                active_player.game_n_oudler += 1
            inactive_player.game_score += inactive_player_card.point
            inactive_player.game_n_oudler += int(inactive_player_card.is_oudler)

        elif isinstance(inactive_player_card, TrumpCard):
            if not isinstance(active_player_card, TrumpCard) or active_player_card.value < inactive_player_card.value:
                winner_id = self.get_inactive_player_ind()
            else:
                winner_id = self.get_active_player_ind()

        else:  # Inactive player played a simple card
            assert isinstance(inactive_player_card, SimpleCard)
            if isinstance(active_player_card, TrumpCard):  # active player cut
                winner_id = self.get_active_player_ind()
            elif active_player_card.suit != inactive_player_card.suit:  # active player could not cut
                winner_id = self.get_inactive_player_ind()
            elif active_player_card.value > inactive_player_card.value:
                winner_id = self.get_active_player_ind()
            else:
                winner_id = self.get_inactive_player_ind()

        if not fool_played:
            winner = self.players[self.player_usernames[winner_id]]
            winner.game_score += sum_card_points - 1
            winner.game_n_oudler += sum_n_oudlers

        return winner_id

    def play_handcard(self, handcard_index: int):
        assert self.active_player_ind is not None
        card = self.get_active_player().hand.cards.pop(handcard_index)
        self._play_card(card=card)
        return card

    def play_tablecard(self, stack_index: int) -> Card:
        assert self.active_player_ind is not None
        card, revealed_card = self.get_active_player().update_stack(stack_index)
        if revealed_card is not None:
            self.cards_to_reveal.append(revealed_card)

        self._play_card(card=card)
        return card

    def refresh_playable_card(self) -> None:
        self.get_inactive_player().set_all_cards_not_playable()

        playing_user = self.get_active_player()
        if self.active_card is not None:
            vs_card = self.active_card
        else:
            vs_card = None
        playing_user.compute_playable_cards(vs_card=vs_card)

    def new_game(self) -> None:
        self.deck = Deck()
        self.active_card = None
        self.active_player_ind = None
        self.cards_to_reveal = []
        self.n_players = 0
        for player in self.players.values():
            player.new_game()
