"""Player logic: the player's actions during a hand."""

import cards
import display
import trainer

ACTION_NAMES = {
    "H": trainer.HIT,
    "S": trainer.STAND,
    "D": trainer.DOUBLE,
    "P": trainer.SPLIT,
    "R": trainer.SURRENDER,
}


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
                     bet, chips_available, tracker=None,
                     allow_split=True, allow_surrender=True):
    """Play one hand.

    chips_available is what the player can still wager beyond current bets
    (needed to double or split). Returns one of:
    "split", "double", "surrender", or "done" (stood, bust or 21).
    """
    first_action = True

    while True:
        display.display_cards(hand, dealer_hand, hide_dealer=True,
                              hand_number=hand_number, bet=bet)
        total = cards.calculate_hand(hand)[0]

        if total >= 21:
            if total == 21:
                print("You have 21.")
            else:
                print("You busted!")
            return "done"

        split_ok = can_split(hand, first_action, allow_split) and chips_available >= bet
        double_ok = can_double(hand, first_action) and chips_available >= bet
        surrender_ok = first_action and allow_surrender and len(hand) == 2

        recommendation, explanation = trainer.coach_advice(
            hand, dealer_hand[0], split_ok, double_ok, surrender_ok
        )

        if coach_enabled:
            print("\nCoach recommends:", recommendation)
            print(explanation)

        action = get_player_action(split_ok, double_ok, surrender_ok,
                                   (recommendation, explanation))

        if tracker is not None:
            tracker.record(
                trainer.describe_situation(hand, dealer_hand[0], split_ok),
                ACTION_NAMES[action],
                recommendation,
            )

        if action == "H":
            new_card = hit(deck, hand)
            print("You drew:", cards.format_card(new_card))
        elif action == "S":
            print("You stand.")
            return "done"
        elif action == "D":
            new_card = double_down(deck, hand)
            print("You doubled down and drew:", cards.format_card(new_card))
            return "double"
        elif action == "P":
            # The caller handles the second hand created by a split.
            return "split"
        elif action == "R":
            return "surrender"

        first_action = False


def get_player_action(can_split, can_double, can_surrender, hint):
    """Ask for an action and reject choices that are not currently allowed.

    Typing ? shows the coach's hint without committing to anything.
    """
    while True:
        choices = ["H", "S"]
        prompt = "Choose [H]it or [S]tand"

        if can_double:
            choices.append("D")
            prompt += ", [D]ouble down"
        if can_split:
            choices.append("P")
            prompt += ", s[P]lit"
        if can_surrender:
            choices.append("R")
            prompt += ", su[R]render"

        choice = input(prompt + " (? for a hint): ").strip().upper()
        if choice == "?":
            print("\nHint:", hint[0])
            print(hint[1])
            continue
        if choice in choices:
            return choice

        print("That action is not available. Please choose a listed action.")