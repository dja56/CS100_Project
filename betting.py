"""Betting: the chip bankroll and bet entry."""

STARTING_CHIPS = 100
MIN_BET = 1


def fmt(amount):
    """Format chips without a trailing .0 (12.0 -> '12', 7.5 -> '7.5')."""
    return format(amount, "g")


class Bankroll:
    """Tracks the player's chips across rounds."""

    def __init__(self, starting=STARTING_CHIPS):
        self.starting = starting
        self.chips = starting
        self.buy_ins = 1

    def settle(self, net):
        """Apply a round's net win (+) or loss (-)."""
        self.chips += net

    def max_bet(self):
        """Bets are whole chips only."""
        return int(self.chips)

    def is_broke(self):
        return self.chips < MIN_BET

    def rebuy(self):
        """Add a fresh stack of starting chips."""
        self.chips += self.starting
        self.buy_ins += 1

    def profit(self):
        """Chips now minus everything bought in so far."""
        return self.chips - self.starting * self.buy_ins


def prompt_bet(bankroll):
    """Ask for a whole-number bet between the minimum and the player's chips."""
    max_bet = bankroll.max_bet()
    while True:
        raw = input("\nChips: " + fmt(bankroll.chips) + ". Enter bet ("
                    + str(MIN_BET) + "-" + str(max_bet) + "): ").strip()
        try:
            bet = int(raw)
        except ValueError:
            print("Enter a whole number.")
            continue

        if bet < MIN_BET or bet > max_bet:
            print("Your bet must be between", MIN_BET, "and", max_bet, "chips.")
            continue
        return bet