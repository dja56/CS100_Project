"""Dealer logic: dealing the dealer's cards and applying the dealer's rules.

Rule: the dealer stands on all 17s, including soft 17.
"""

from player import calculate_hand, format_card


def deal_dealer_hand(deck):
    """Deal two cards to the dealer."""
    return [deck.pop(), deck.pop()]


def dealer_should_hit(dealer_hand):
    """The dealer hits until reaching 17 or higher."""
    return calculate_hand(dealer_hand)[0] < 17


def dealer_turn(deck, dealer_hand):
    """Play out the dealer's hand, printing each draw."""
    print("\nDealer's turn:")
    while dealer_should_hit(dealer_hand):
        new_card = deck.pop()
        dealer_hand.append(new_card)
        print("Dealer draws:", format_card(new_card))

    total, soft = calculate_hand(dealer_hand)
    print("Dealer stands at", total, "(soft)" if soft else "")