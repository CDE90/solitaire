import random
from itertools import product
from typing import Final, Literal

type Suit = Literal[1, 2, 3, 4]
type Value = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

SUITS_MAP: dict[Suit, tuple[str, str]] = {
    1: ("Hearts", "♥"),
    2: ("Clubs", "♣"),
    3: ("Diamonds", "♦"),
    4: ("Spades", "♠"),
}
VALUES_MAP: dict[Value, tuple[str, str]] = {
    1: ("Ace", "A"),
    2: ("Two", "2"),
    3: ("Three", "3"),
    4: ("Four", "4"),
    5: ("Five", "5"),
    6: ("Six", "6"),
    7: ("Seven", "7"),
    8: ("Eight", "8"),
    9: ("Nine", "9"),
    10: ("Ten", "10"),
    11: ("Jack", "J"),
    12: ("Queen", "Q"),
    13: ("King", "K"),
}


class Card:
    def __init__(self, value: Value, suit: Suit) -> None:
        self.value: Final[Value] = value
        self.suit: Final[Suit] = suit

    def __repr__(self) -> str:
        return f"Card({self.value}, {self.suit})"

    def __str__(self) -> str:
        # return f"{VALUES_MAP[self.value][1]}{SUITS_MAP[self.suit][1]}"
        # display with ANSI colors
        suit_symbol = SUITS_MAP[self.suit][1]
        if self.suit in (1, 3):  # Hearts and Diamonds are red
            return f"\033[91m{VALUES_MAP[self.value][1]}{suit_symbol}\033[0m"
        else:  # Clubs and Spades are black
            return f"\033[90m{VALUES_MAP[self.value][1]}{suit_symbol}\033[0m"


class BlankCard:
    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return "BlankCard()"

    def __str__(self) -> str:
        # return "XX"
        # display with regular ansi black (not high intensity)
        return "\033[94mXX\033[0m"


BLANK = BlankCard()


class Deck:
    def __init__(self) -> None:
        self.cards: list[Card] = [
            Card(v, s) for s, v in product(SUITS_MAP.keys(), VALUES_MAP.keys())
        ]

    def __repr__(self) -> str:
        return f"Deck({self.cards})"

    def __str__(self) -> str:
        return "[" + ", ".join(str(card) for card in self.cards) + "]"

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def peek(self) -> Card:
        if self.is_empty():
            raise IndexError("Cannot peek at an empty deck")
        return self.cards[-1]

    def draw(self) -> Card:
        if self.is_empty():
            raise IndexError("Cannot draw from an empty deck")
        return self.cards.pop()

    def is_empty(self) -> bool:
        return len(self.cards) == 0
