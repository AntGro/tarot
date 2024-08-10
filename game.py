# game.py
from __future__ import annotations

import enum
import random
from abc import ABC, abstractmethod
from typing import Dict, List

from pydantic import BaseModel, field_validator, computed_field, Field


class Card(BaseModel, ABC):
    is_face_down: bool = False

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


class TrumpCard(Card):
    value: int

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

    @computed_field
    def _path(self) -> str:
        if self.value <= 10:
            val = self.value if self.value > 1 else "ace"
        elif self.value == 11:
            val = "jack"
        elif self.value == 12:
            val = "knight"
        elif self.value == 13:
            val = "queen"
        elif self.value == 14:
            val = "king"
        else:
            raise ValueError(self.value)
        return f"/static/images/{val}_of_{self.suit.value}.png"

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


class CardHand(BaseModel):
    cards: List[Card]

    def model_post_init(self, __context):
        self.cards = sorted(self.cards)


class Player(BaseModel):
    username: str
    hand: CardHand
    cards_on_table: List[CardStack]


class CardGame(BaseModel):
    deck: Deck = Field(default_factory=Deck)
    players: Dict[str, Player] = {}

    def model_post_init(self, __context):
        self.deck = Deck()
        self.players = {}

    def shuffle_deck(self):
        self.deck.shuffle()

    def deal_cards(self, username):
        self.shuffle_deck()
        stacks = []
        for i in range(7):
            stack = CardStack(cards=self.deck.deal(i + 1))
            stacks.append(stack)

        self.players[username] = Player(username=username, hand=CardHand(cards=self.deck.deal(11)),
                                        cards_on_table=stacks)
        return


if __name__ == "__main__":
    game = CardGame()
    game.deal_cards(7)
    print(game)
