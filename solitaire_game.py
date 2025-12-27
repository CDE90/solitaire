from deck import BLANK, Card, Deck


class SolitaireGame:
    def __init__(self, n_draw: int = 3) -> None:
        # number of cards to draw from the stock at a time
        self.n_draw = n_draw

        self.deck = Deck()
        self.tableau: list[list[tuple[Card, bool]]] = [[] for _ in range(7)]
        self.foundation: list[list[Card]] = [[] for _ in range(4)]
        self.stock: list[Card] = []
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

        # Draw the remaining cards into the stock
        while not self.deck.is_empty():
            self.stock.append(self.deck.draw())

    def __str__(self) -> str:
        result = "Tableau:\n"
        for i, pile in enumerate(self.tableau):
            if pile:
                cards_str = []
                for card, is_face_up in pile:
                    if is_face_up:
                        cards_str.append(str(card))
                    else:
                        cards_str.append(str(BLANK))
                result += f"Pile {i + 1}: " + ", ".join(cards_str) + "\n"
            else:
                result += f"Pile {i + 1}: \n"

        result += "Foundation:\n"
        for i, pile in enumerate(self.foundation):
            result += f"Pile {i + 1}: " + ", ".join(str(card) for card in pile) + "\n"

        result += "Waste: " + ", ".join(str(card) for card in self.waste) + "\n"

        result += "Stock: " + str(len(self.stock)) + " cards remaining\n"

        return result

    # Game logic and movement methods:

    def move_tableau_to_foundation(self, tableau_index: int) -> None:
        if not self.tableau[tableau_index]:
            raise ValueError("No cards in the selected tableau pile")
        card, _ = self.tableau[tableau_index][-1]
        foundation_pile = self.foundation[card.suit - 1]
        if (not foundation_pile and card.value == 1) or (
            foundation_pile and card.value == foundation_pile[-1].value + 1
        ):
            self.tableau[tableau_index].pop()
            foundation_pile.append(card)
            if self.tableau[tableau_index]:
                new_top_card, _ = self.tableau[tableau_index][-1]
                self.tableau[tableau_index][-1] = (new_top_card, True)
        else:
            raise ValueError("Invalid move to foundation")

    def move_tableau_to_tableau(
        self, from_index: int, to_index: int, num_cards: int
    ) -> None:
        if len(self.tableau[from_index]) < num_cards:
            raise ValueError("Not enough cards in the selected tableau pile")
        moving_cards = self.tableau[from_index][-num_cards:]

        if not moving_cards[0][1]:
            raise ValueError("Cannot move face-down cards")

        if self.is_valid_tableau_move(moving_cards[0][0], to_index):
            self.tableau[from_index] = self.tableau[from_index][:-num_cards]
            self.tableau[to_index].extend(moving_cards)
            if self.tableau[from_index]:
                new_top_card, _ = self.tableau[from_index][-1]
                self.tableau[from_index][-1] = (new_top_card, True)
        else:
            raise ValueError("Invalid move to tableau")

    def draw_from_stock(self) -> None:
        if not self.stock:
            # recycle waste into stock
            self.stock = self.waste[::-1]
            self.waste.clear()

        for _ in range(self.n_draw):
            if self.stock:
                card = self.stock.pop()
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
        if self.is_valid_tableau_move(card, tableau_index):
            self.waste.pop()
            self.tableau[tableau_index].append((card, True))
        else:
            raise ValueError("Invalid move to tableau")

    def foundation_to_tableau(self, foundation_index: int, tableau_index: int) -> None:
        if not self.foundation[foundation_index]:
            raise ValueError("No cards in the selected foundation pile")
        card = self.foundation[foundation_index][-1]
        if self.is_valid_tableau_move(card, tableau_index):
            self.foundation[foundation_index].pop()
            self.tableau[tableau_index].append((card, True))
        else:
            raise ValueError("Invalid move to tableau")

    def is_valid_tableau_move(self, card: Card, to_index: int) -> bool:
        if not self.tableau[to_index]:
            return card.value == 13  # Only Kings can be placed on empty tableau piles
        dest_card, _ = self.tableau[to_index][-1]
        # Check for alternating colors and descending order
        if (card.suit in (1, 3) and dest_card.suit in (2, 4)) or (
            card.suit in (2, 4) and dest_card.suit in (1, 3)
        ):
            return card.value == dest_card.value - 1
        return False

    def is_game_won(self) -> bool:
        return (
            all(len(pile) == 13 for pile in self.foundation)
            or self.can_be_auto_solved()
        )

    def can_be_auto_solved(self) -> bool:
        # A simple heuristic: if all cards in the tableau are face up
        # and there is either 0 or 1 card in the stock/waste combined,
        # we can consider it solvable.
        for pile in self.tableau:
            for _, is_face_up in pile:
                if not is_face_up:
                    return False
        if len(self.stock) + len(self.waste) > 1:
            return False
        return True

    def reset_game(self) -> None:
        self.deck = Deck()
        self.tableau = [[] for _ in range(7)]
        self.foundation = [[] for _ in range(4)]
        self.stock = []
        self.waste = []
        self.setup_game()

    def list_valid_moves(self) -> list[str]:
        moves = []
        # Check waste to foundation
        if self.waste:
            card = self.waste[-1]
            foundation_pile = self.foundation[card.suit - 1]
            if (not foundation_pile and card.value == 1) or (
                foundation_pile and card.value == foundation_pile[-1].value + 1
            ):
                moves.append("Waste to Foundation")

        # Check waste to tableau
        if self.waste:
            card = self.waste[-1]
            for i in range(7):
                if self.is_valid_tableau_move(card, i):
                    moves.append(f"Waste to Tableau {i + 1}")

        # Check tableau to foundation
        for i in range(7):
            if self.tableau[i]:
                card, _ = self.tableau[i][-1]
                foundation_pile = self.foundation[card.suit - 1]
                if (not foundation_pile and card.value == 1) or (
                    foundation_pile and card.value == foundation_pile[-1].value + 1
                ):
                    moves.append(f"Tableau {i + 1} to Foundation")

        # Check tableau to tableau
        for from_idx in range(7):
            for to_idx in range(7):
                if from_idx != to_idx:
                    for n in range(1, len(self.tableau[from_idx]) + 1):
                        moving_cards = self.tableau[from_idx][-n:]
                        # We can only move cards that are face up
                        if not moving_cards[0][1]:
                            break
                        if self.is_valid_tableau_move(moving_cards[0][0], to_idx):
                            moves.append(
                                f"Tableau {from_idx + 1} to Tableau {to_idx + 1} ({n} cards)"
                            )

        return moves


def main():
    game = SolitaireGame()
    while True:
        print("\n" + "=" * 40)
        print(game)
        if game.is_game_won():
            print("Congratulations! You won!")
            break

        print("\nCommands:")
        print("  s          : Draw from stock")
        print("  wf         : Move waste to foundation")
        print("  wt <T>     : Move waste to tableau pile <T>")
        print("  tf <T>     : Move tableau pile <T> to foundation")
        print("  ft <F> <T> : Move foundation <F> to tableau pile <T>")
        print("  tt <F> <T> <N>: Move <N> cards from tableau <F> to <T>")
        print("  q          : Quit")

        valid_moves = game.list_valid_moves()
        if valid_moves:
            print("\nValid moves:")
            for move in valid_moves:
                print(f"  {move}")

        command = input("\nEnter command: ").strip().lower().split()
        if not command:
            continue

        cmd = command[0]
        try:
            if cmd == "q":
                print("Thanks for playing!")
                break
            elif cmd == "s":
                game.draw_from_stock()
            elif cmd == "wf":
                game.move_waste_to_foundation()
            elif cmd == "wt":
                if len(command) != 2:
                    print("Usage: wt <tableau_index>")
                    continue
                t_idx = int(command[1]) - 1
                game.move_waste_to_tableau(t_idx)
            elif cmd == "tf":
                if len(command) != 2:
                    print("Usage: tf <tableau_index>")
                    continue
                t_idx = int(command[1]) - 1
                game.move_tableau_to_foundation(t_idx)
            elif cmd == "ft":
                if len(command) != 3:
                    print("Usage: ft <foundation_index> <tableau_index>")
                    continue
                f_idx = int(command[1]) - 1
                t_idx = int(command[2]) - 1
                game.foundation_to_tableau(f_idx, t_idx)
            elif cmd == "tt":
                if len(command) != 4:
                    print("Usage: tt <from_index> <to_index> <num_cards>")
                    continue
                f_idx = int(command[1]) - 1
                t_idx = int(command[2]) - 1
                n = int(command[3])
                game.move_tableau_to_tableau(f_idx, t_idx, n)
            else:
                print("Unknown command.")
        except (ValueError, IndexError) as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
