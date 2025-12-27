from deck import BLANK, Card, Deck


class SolitaireGame:
    def __init__(self, n_draw: int = 3) -> None:
        # number of cards to draw from the deck at a time
        self.n_draw = n_draw

        self.deck = Deck()
        self.tableau: list[list[tuple[Card, bool]]] = [[] for _ in range(7)]
        self.foundation: list[list[Card]] = [[] for _ in range(4)]
        self.waste: list[Card] = []

        self.setup_game()

    def setup_game(self) -> None:
        self.deck.shuffle()
        for i in range(7):
            for j in range(i, 7):
                card = self.deck.draw()
                # self.tableau[j].append(card)
                # we store a tuple of (Card, is_face_up)
                is_face_up = i == j  # only the top card is face up
                self.tableau[j].append((card, is_face_up))

    def __str__(self) -> str:
        result = "Tableau:\n"
        for i, pile in enumerate(self.tableau):
            if pile:
                result += (
                    f"Pile {i + 1}: "
                    + ", ".join(str(BLANK) for _ in pile[:-1])
                    + (", " if len(pile) > 1 else "")
                    + f"{str(pile[-1])}\n"
                )
            else:
                result += f"Pile {i + 1}: \n"
        result += "Foundation:\n"
        for i, pile in enumerate(self.foundation):
            result += f"Pile {i + 1}: " + ", ".join(str(card) for card in pile) + "\n"
        result += "Waste: " + ", ".join(str(card) for card in self.waste) + "\n"
        result += "Deck: " + str(len(self.deck.cards)) + " cards remaining\n"
        return result

    # Game logic and movement methods:

    def move_tableau_to_foundation(self, tableau_index: int) -> None:
        if not self.tableau[tableau_index]:
            raise ValueError("No cards in the selected tableau pile")
        card = self.tableau[tableau_index][-1]
        foundation_pile = self.foundation[card.suit - 1]
        if (not foundation_pile and card.value == 1) or (
            foundation_pile and card.value == foundation_pile[-1].value + 1
        ):
            self.tableau[tableau_index].pop()
            foundation_pile.append(card)
        else:
            raise ValueError("Invalid move to foundation")

    def move_tableau_to_tableau(
        self, from_index: int, to_index: int, num_cards: int
    ) -> None:
        if len(self.tableau[from_index]) < num_cards:
            raise ValueError("Not enough cards in the selected tableau pile")
        moving_cards = self.tableau[from_index][-num_cards:]
        if self.is_valid_tableau_move(moving_cards, to_index):
            self.tableau[from_index] = self.tableau[from_index][:-num_cards]
            self.tableau[to_index].extend(moving_cards)
        else:
            raise ValueError("Invalid move to tableau")

    def draw_from_deck(self) -> None:
        if self.deck.is_empty():
            raise ValueError("Deck is empty")

        for _ in range(self.n_draw):
            if not self.deck.is_empty():
                card = self.deck.draw()
                self.waste.append(card)

    def move_waste_to_foundation(self) -> None:
        if not self.waste:
            raise ValueError("No cards in the waste pile")
        card = self.waste[-1]
        foundation_pile = self.foundation[card.suit - 1]
        if (not foundation_pile and card.value == 1) or (
            foundation_pile and card.value == foundation_pile[-1].value + 1
        ):
            self.waste.pop()
            foundation_pile.append(card)
        else:
            raise ValueError("Invalid move to foundation")

    def move_waste_to_tableau(self, tableau_index: int) -> None:
        if not self.waste:
            raise ValueError("No cards in the waste pile")
        card = self.waste[-1]
        if self.is_valid_tableau_move([card], tableau_index):
            self.waste.pop()
            self.tableau[tableau_index].append(card)
        else:
            raise ValueError("Invalid move to tableau")

    def is_valid_tableau_move(self, moving_cards: list[Card], to_index: int) -> bool:
        if not moving_cards:
            return False
        top_card = moving_cards[0]
        if not self.tableau[to_index]:
            return (
                top_card.value == 13
            )  # Only Kings can be placed on empty tableau piles
        dest_card = self.tableau[to_index][-1]
        # Check for alternating colors and descending order
        if (top_card.suit in (1, 3) and dest_card.suit in (2, 4)) or (
            top_card.suit in (2, 4) and dest_card.suit in (1, 3)
        ):
            return top_card.value == dest_card.value - 1
        return False

    def is_game_won(self) -> bool:
        return all(len(pile) == 13 for pile in self.foundation)


if __name__ == "__main__":
    game = SolitaireGame()
    print(game)
