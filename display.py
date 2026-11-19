"""Text display for hands."""

import cards
from betting import fmt


def display_player_hand(hand, hand_number=None, bet=None):
    """Print one player hand, with an optional hand header and bet."""
    if hand_number is not None:
        header = "--- Player Hand " + str(hand_number)
        if bet is not None:
            header += " (bet " + fmt(bet) + ")"
        print("\n" + header + " ---")

    print("Your cards:")
    for card in hand:
        print("  " + cards.format_card(card))

    total, soft = cards.calculate_hand(hand)
    print("Your total:", str(total) + (" (soft)" if soft else ""))


def display_dealer_hand(dealer_hand, hide_dealer=True):
    """Print the dealer's hand, hiding the hole card if requested."""
    print("\nDealer's cards:")
    if hide_dealer:
        print("  " + cards.format_card(dealer_hand[0]))
        print("  [Hidden card]")
    else:
        for card in dealer_hand:
            print("  " + cards.format_card(card))
        total, soft = cards.calculate_hand(dealer_hand)
        print("Dealer total:", str(total) + (" (soft)" if soft else ""))


def display_cards(player_hand, dealer_hand, hide_dealer=True,
                  hand_number=None, bet=None):
    """Display the player's hand and the dealer's hand."""
    display_player_hand(player_hand, hand_number, bet)
    display_dealer_hand(dealer_hand, hide_dealer)