"""Cards and hand math shared by every module."""

import random

RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10",
         "J", "Q", "K", "A"]
SUITS = ["spade", "club", "heart", "diamond"]


def create_deck():
    """Create and shuffle a standard deck of 52 cards."""
    deck = []
    for suit in SUITS:
        for rank in RANKS:
            deck.append({"rank": rank, "suit": suit})

    random.shuffle(deck)
    return deck


def card_value(card):
    """Return the blackjack value of one card (Ace counts as 11 here)."""
    rank = card["rank"]

    if rank in ["J", "Q", "K"]:
        return 10
    if rank == "A":
        return 11
    return int(rank)


def calculate_hand(hand):
    """Return (total, soft), where soft means an Ace is currently counted as 11."""
    total = sum(card_value(card) for card in hand)
    aces = sum(1 for card in hand if card["rank"] == "A")

    while total > 21 and aces > 0:
        total -= 10
        aces -= 1

    # An Ace is soft if at least one Ace is still being counted as 11.
    soft = aces > 0
    return total, soft


def format_card(card):
    return card["rank"] + " of " + card["suit"]


def is_blackjack(hand):
    """A natural: exactly two cards totalling 21."""
    return len(hand) == 2 and calculate_hand(hand)[0] == 21