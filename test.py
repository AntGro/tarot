import json

from game import SimpleCard, Suit, TrumpCard, Deck


def test_json():
    simple_card = SimpleCard(5, Suit.HEARTS)
    print(json.dumps(simple_card.to_dict()))
    trump_card = TrumpCard(5)
    print(json.dumps(trump_card.to_dict()))
    deck = Deck()
    for card in deck.cards[::-1]:
        print(json.dumps(card))


if __name__ == "__main__":
    test_json()