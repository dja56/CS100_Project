"""Dealer logic: dealing the dealer's cards and applying the dealer's rules.

Rule: the dealer stands on all 17s, including soft 17.
"""

import cards


def deal_dealer_hand(deck):
    """Deal two cards to the dealer."""
    return [deck.pop(), deck.pop()]


def shows_ace(dealer_hand):
    """True if the dealer's up-card is an Ace (insurance is offered)."""
    return dealer_hand[0]["rank"] == "A"


def shows_ten_or_ace(dealer_hand):
    """True if the dealer must check the hole card for Blackjack."""
    return shows_ace(dealer_hand) or cards.card_value(dealer_hand[0]) == 10


def has_blackjack(dealer_hand):
    return cards.is_blackjack(dealer_hand)


def dealer_should_hit(dealer_hand):
    """The dealer hits until reaching 17 or higher."""
    return cards.calculate_hand(dealer_hand)[0] < 17


def dealer_turn(deck, dealer_hand):
    """Play out the dealer's hand, printing each draw."""
    print("\nDealer's turn:")
    while dealer_should_hit(dealer_hand):
        new_card = deck.pop()
        dealer_hand.append(new_card)
        print("Dealer draws:", cards.format_card(new_card))

    total, soft = cards.calculate_hand(dealer_hand)
    if total > 21:
        print("Dealer busts with", total)
    else:
        print("Dealer stands at", total, "(soft)" if soft else "")