"""Player logic: card values, hand totals, and the player's actions."""


def card_value(card):
    """Return the blackjack value of one card before Ace adjustment."""
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


def can_split(hand, first_action=True, allow_split=True):
    """A hand can be split on its first action if it holds two cards of the same rank."""
    return (
        allow_split
        and first_action
        and len(hand) == 2
        and hand[0]["rank"] == hand[1]["rank"]
    )


def can_double(hand, first_action=True):
    """A hand can be doubled on its first two cards."""
    return first_action and len(hand) == 2


def hit(deck, hand):
    """Draw one card into the hand and return it."""
    card = deck.pop()
    hand.append(card)
    return card


def double_down(deck, hand):
    """Draw exactly one card and return it. The hand is then finished."""
    return hit(deck, hand)


def split_hand(deck, hand):
    """Split a pair into two hands, dealing one new card to each.

    Returns (first_hand, second_hand).
    """
    first_hand = [hand[0], deck.pop()]
    second_hand = [hand[1], deck.pop()]
    return first_hand, second_hand