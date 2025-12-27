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
        for i, t_pile in enumerate(self.tableau):
            if t_pile:
                cards_str = []
                for card, is_face_up in t_pile:
                    if is_face_up:
                        cards_str.append(str(card))
                    else:
                        cards_str.append(str(BLANK))
                result += f"Pile {i + 1}: " + ", ".join(cards_str) + "\n"
            else:
                result += f"Pile {i + 1}: \n"

        result += "Foundation:\n"
        for i, f_pile in enumerate(self.foundation):
            result += f"Pile {i + 1}: " + ", ".join(str(card) for card in f_pile) + "\n"

        result += "Waste: " + ", ".join(str(card) for card in self.waste) + "\n"

        result += "Stock: " + str(len(self.stock)) + " cards remaining\n"

        return result

    # Game logic and movement methods:

    def move_tableau_to_foundation(self, tableau_index: int) -> None:
        if not self.tableau[tableau_index]:
            raise ValueError("No cards in the selected tableau pile")
        card, _ = self.tableau[tableau_index][-1]
        foundation_pile = self.foundation[card.suit - 1]
        if (not foundation_pile and card.rank == 1) or (
            foundation_pile and card.rank == foundation_pile[-1].rank + 1
        ):
            self.tableau[tableau_index].pop()
            foundation_pile.append(card)
            if self.tableau[tableau_index]:
                new_top_card, _ = self.tableau[tableau_index][-1]
                self.tableau[tableau_index][-1] = (new_top_card, True)
        else:
            raise ValueError("Invalid move to foundation")

    def move_tableau_to_tableau(self, from_index: int, to_index: int) -> None:
        if not self.tableau[from_index]:
            raise ValueError("No cards in the selected tableau pile")

        # Find the deepest face-up card that can be moved to to_index
        valid_num_cards = 0
        found_move = False
        source_pile = self.tableau[from_index]

        for i in range(len(source_pile)):
            card, is_face_up = source_pile[i]
            if is_face_up:
                if self.is_valid_tableau_move(card, to_index):
                    valid_num_cards = len(source_pile) - i
                    found_move = True
                    break

        if not found_move:
            raise ValueError("Invalid move to tableau")

        num_cards = valid_num_cards
        moving_cards = self.tableau[from_index][-num_cards:]

        self.tableau[from_index] = self.tableau[from_index][:-num_cards]
        self.tableau[to_index].extend(moving_cards)
        if self.tableau[from_index]:
            new_top_card, _ = self.tableau[from_index][-1]
            self.tableau[from_index][-1] = (new_top_card, True)

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
        if (not foundation_pile and card.rank == 1) or (
            foundation_pile and card.rank == foundation_pile[-1].rank + 1
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
            return card.rank == 13  # Only Kings can be placed on empty tableau piles
        dest_card, _ = self.tableau[to_index][-1]
        # Check for alternating colors and descending order
        if (card.suit in (1, 3) and dest_card.suit in (2, 4)) or (
            card.suit in (2, 4) and dest_card.suit in (1, 3)
        ):
            return card.rank == dest_card.rank - 1
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

    def get_game_state(self) -> bytes:
        """
        Returns a hashable bytes representation of the current game state.
        Format:
        - Stock Length (1 byte)
        - Stock Cards (N bytes)
        - Waste Length (1 byte)
        - Waste Cards (M bytes)
        - Foundation Counts (4 bytes)
        - Tableau (7 piles):
            - Pile Length (1 byte)
            - Cards (K bytes, bit 6 set if face up)
        """
        data = bytearray()

        # Stock
        data.append(len(self.stock))
        for card in self.stock:
            data.append(self._card_to_int(card))

        # Waste
        data.append(len(self.waste))
        for card in self.waste:
            data.append(self._card_to_int(card))

        # Foundation
        for f_pile in self.foundation:
            data.append(len(f_pile))

        # Tableau
        for t_pile in self.tableau:
            data.append(len(t_pile))
            for card, is_face_up in t_pile:
                data.append(self._encode_tableau_card(card, is_face_up))

        return bytes(data)

    def set_game_state(self, state: bytes) -> None:
        """
        Restores the game state from a bytes representation.
        """
        data = memoryview(state)
        idx = 0

        # Stock
        stock_len = data[idx]
        idx += 1
        self.stock = [self._int_to_card(data[i]) for i in range(idx, idx + stock_len)]
        idx += stock_len

        # Waste
        waste_len = data[idx]
        idx += 1
        self.waste = [self._int_to_card(data[i]) for i in range(idx, idx + waste_len)]
        idx += waste_len

        # Foundation
        self.foundation = []
        for suit_offset in range(4):
            count = data[idx]
            idx += 1
            suit = suit_offset + 1
            f_pile = [Card(rank, suit) for rank in range(1, count + 1)]  # type: ignore
            self.foundation.append(f_pile)

        # Tableau
        self.tableau = []
        for _ in range(7):
            pile_len = data[idx]
            idx += 1
            t_pile = []
            for i in range(idx, idx + pile_len):
                t_pile.append(self._decode_tableau_card(data[i]))
            self.tableau.append(t_pile)
            idx += pile_len

    def _card_to_int(self, card: Card) -> int:
        # Bits 0-3: Rank (0-12)
        # Bits 4-5: Suit (0-3)
        return ((card.suit - 1) << 4) | (card.rank - 1)

    def _int_to_card(self, value: int) -> Card:
        # Mask 0xF (1111 binary) gets the first 4 bits
        rank = (value & 0xF) + 1
        # Shift right 4 and mask 0x3 (11 binary) gets the next 2 bits
        suit = ((value >> 4) & 0x3) + 1
        return Card(rank, suit)  # type: ignore

    def _encode_tableau_card(self, card: Card, is_face_up: bool) -> int:
        val = self._card_to_int(card)
        if is_face_up:
            # Set bit 6
            val |= 1 << 6
        return val

    def _decode_tableau_card(self, value: int) -> tuple[Card, bool]:
        # Check bit 6
        is_face_up = bool((value >> 6) & 1)
        # Clear bit 6 to get the card value
        card_val = value & ~(1 << 6)
        return self._int_to_card(card_val), is_face_up

    def list_valid_moves(self) -> list[str]:
        moves = []
        # Check waste to foundation
        if self.waste:
            card = self.waste[-1]
            foundation_pile = self.foundation[card.suit - 1]
            if (not foundation_pile and card.rank == 1) or (
                foundation_pile and card.rank == foundation_pile[-1].rank + 1
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
                if (not foundation_pile and card.rank == 1) or (
                    foundation_pile and card.rank == foundation_pile[-1].rank + 1
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

        # Check foundation to tableau
        for f_idx in range(4):
            if self.foundation[f_idx]:
                card = self.foundation[f_idx][-1]
                for t_idx in range(7):
                    if self.is_valid_tableau_move(card, t_idx):
                        moves.append(f"Foundation {f_idx + 1} to Tableau {t_idx + 1}")

        # Check draw from stock
        if self.stock or self.waste:
            moves.append("Draw from Stock")

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
        print("  tt <F> <T> : Move cards from tableau <F> to <T>")
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
                if len(command) != 3:
                    print("Usage: tt <from_index> <to_index>")
                    continue
                f_idx = int(command[1]) - 1
                t_idx = int(command[2]) - 1
                game.move_tableau_to_tableau(f_idx, t_idx)
            else:
                print("Unknown command.")
        except (ValueError, IndexError) as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
