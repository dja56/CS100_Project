import trainer
import main


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

def play_player_hand(deck, hand, dealer_hand, hand_number, coach_enabled,
                     allow_split=True, split_aces=False):
    """Play one hand. Returns "split" if the player splits, otherwise whether it was doubled."""
    first_action = True

    while True:
        main.display_cards(hand, dealer_hand, hide_dealer=True, hand_number=hand_number)
        total = calculate_hand(hand)[0]

        if total >= 21:
            if total == 21:
                print("You have 21.")
            else:
                print("You busted!")
            return False

        if split_aces:
            print("Split Aces receive only one card. This hand is finished.")
            return False

        split_ok = can_split(hand, first_action, allow_split)
        double_ok = can_double(hand, first_action)

        if coach_enabled:
            recommendation, explanation = trainer.coach_advice(
                hand, dealer_hand[0], split_ok, double_ok
            )
            print("\nCoach recommends:", recommendation)
            print(explanation)

        action = get_player_action(split_ok, double_ok)

        if action == "H":
            new_card = hit(deck, hand)
            print("You drew:", format_card(new_card))
        elif action == "S":
            print("You stand.")
            return False
        elif action == "D":
            new_card = double_down(deck, hand)
            print("You doubled down and drew:", format_card(new_card))
            return True
        elif action == "P":
            # The caller handles the second hand created by a split.
            return "split"

        first_action = False

def get_player_action(can_split, can_double):
    """Ask for an action and reject choices that are not currently allowed."""
    while True:
        choices = ["H", "S"]
        prompt = "Choose [H]it or [S]tand"

        if can_double:
            choices.append("D")
            prompt += ", [D]ouble down"
        if can_split:
            choices.append("P")
            prompt += ", s[P]lit"

        choice = input(prompt + ": ").strip().upper()
        if choice in choices:
            return choice

        print("That action is not available. Please choose a listed action.")