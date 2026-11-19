"""Trainer: beginner-friendly basic-strategy recommendations and explanations."""

from collections import Counter

import cards

HIT = "HIT"
STAND = "STAND"
DOUBLE = "DOUBLE"
SPLIT = "SPLIT"
SURRENDER = "SURRENDER"
TAKE_INSURANCE = "TAKE INSURANCE"
DECLINE_INSURANCE = "DECLINE INSURANCE"

def _dealer_note(d):
    if d <= 6:
        return "The dealer shows a weak card (2-6) and busts often"
    return "The dealer shows a strong card (7-A) and rarely busts"

def _double_or(can_double, fallback, why):
    """Recommend Double, or the fallback action if doubling isn't available"""
    if can_double:
        return DOUBLE, why
    return fallback, why + "Doubling isn't available here, so " + fallback.lower() + " instead."

def describe_situation(hand, dealer_up_card, can_split=False):
    """Short for a decision, e.g. 'Hard 16 vs dealer 10'"""
    total, soft = cards.calculate_hand(hand)
    if can_split and len(hand) == 2 and hand[0]["rank"] == hand[1]["rank"]:
        label = "Pair of " + hand[0]["rank"] + "s"
    elif soft:
        label = "Soft " + str(total)
    else:
        label = "Hard " + str(total)
    return label + " vs dealer " + dealer_up_card["rank"]

def _pair_advice(rank, d):
    """Pair-splitting chart. Returns None when the pair should be played as a normal total."""
    if rank == "A":
        return SPLIT, "Always split Aces. One Ace is a strong start; two together as 12 is weak."
    if rank == "8":
        return SPLIT, "Always split 8s. A hard 16 is the worst hand, and two fresh 8s are much better."
    if rank in ["10", "J", "Q", "K"]:
        return STAND, "A pair worth 20 is already a very strong hand. Do not split it."
    if rank == "9":
        if d in [7, 10, 11]:
            return STAND, ("An 18 beats a dealer 7 (who usually ends on 17), and 10 or Ace "
                           "is too strong to risk splitting into.")
        return SPLIT, "Split 9s against 2-6, 8 or 9. Two hands starting at 9 beat one 18."
    if rank == "7":
        if d <= 7:
            return SPLIT, "Split 7s against a dealer 2-7. A hard 14 is weak, but two 7s have potential."
        return None
    if rank == "6":
        if d <= 6:
            return SPLIT, "Split 6s against a dealer 2-6. A hard 12 is weak, and the dealer is vulnerable."
        return None
    if rank in ["2", "3"]:
        if d <= 7:
            return SPLIT, "Split 2s and 3s against a dealer 2-7 to turn a weak total into two better starts."
        return None
    if rank == "4":
        if d in [5, 6]:
            return SPLIT, "Split 4s only against a dealer 5 or 6, the dealer's weakest cards."
        return None
    return None  # 5s are played as a hard 10

def _surrender_advice(total, d):
    """Late-surrender chart (dealer stands on soft 17). Hard hands only."""
    if total == 16 and d in [9, 10, 11]:
        return SURRENDER, ("Hard 16 against a 9, 10 or Ace loses most of the time. "
                           "Giving up half your bet costs less on average than playing it out.")
    if total == 15 and d == 10:
        return SURRENDER, ("Hard 15 against a 10 is one of the worst spots in blackjack. "
                           "Surrendering saves half your bet on average.")
    return None


def _soft_advice(total, d, can_double):
    if total >= 19:
        return STAND, "Soft 19 or better is already a strong hand."
    if total == 18:
        if 3 <= d <= 6:
            return _double_or(can_double, STAND,
                              "Soft 18 against a weak dealer card is a good doubling spot.")
        if d in [2, 7, 8]:
            return STAND, "Soft 18 is good enough against a dealer 2, 7 or 8."
        return HIT, "Soft 18 loses to a dealer 9, 10 or Ace, and you can't bust with one card."
    if total == 17:
        if 3 <= d <= 6:
            return _double_or(can_double, HIT,
                              "Soft 17 can take one card safely, so double against a weak dealer card.")
        return HIT, "Soft 17 is too weak to stand on, and you can't bust with one card."
    if total in [15, 16]:
        if 4 <= d <= 6:
            return _double_or(can_double, HIT,
                              "Soft 15 or 16 can double against a dealer 4-6 because the dealer is weak.")
        return HIT, "A soft total this low should keep drawing; you can't bust with one card."
    if total in [13, 14]:
        if 5 <= d <= 6:
            return _double_or(can_double, HIT,
                              "Soft 13 or 14 can double against a dealer 5 or 6, the weakest cards.")
        return HIT, "A soft total this low should keep drawing; you can't bust with one card."
    return HIT, "A soft total this low should keep drawing; you can't bust with one card."


def _hard_advice(total, d, can_double):
    if total >= 17:
        return STAND, "A hard 17 or higher is a stand; hitting risks busting for little gain."
    if total >= 13:
        if d <= 6:
            return STAND, "The dealer has a weak up-card. Let the dealer take the risk of busting."
        return HIT, "The dealer has a strong up-card, so you need to improve even though you might bust."
    if total == 12:
        if d in [4, 5, 6]:
            return STAND, "A hard 12 stands against a dealer 4, 5 or 6, who bust most often."
        return HIT, "A hard 12 is too weak against this dealer card, so take another card."
    if total == 11:
        if d <= 10:
            return _double_or(can_double, HIT,
                              "11 is the best doubling total: any 10-value card gives you 21.")
        return HIT, "Against an Ace the dealer is strong enough that hitting is better than doubling."
    if total == 10:
        if d <= 9:
            return _double_or(can_double, HIT,
                              "10 is a strong doubling total against a dealer 2-9.")
        return HIT, "Against a 10 or Ace, doubling a 10 is too risky. Just hit."
    if total == 9:
        if 3 <= d <= 6:
            return _double_or(can_double, HIT,
                              "9 can double against a dealer 3-6 when the dealer is weak.")
        return HIT, "A 9 is only worth doubling against a weak dealer 3-6. Otherwise hit."
    return HIT, "Your total is low and can't bust on one card, so keep drawing."


def coach_advice(hand, dealer_up_card, can_split, can_double, can_surrender=False):
    """Return (action, explanation) following basic strategy."""
    total, soft = cards.calculate_hand(hand)
    d = cards.card_value(dealer_up_card)

    if can_split and len(hand) == 2 and hand[0]["rank"] == hand[1]["rank"]:
        advice = _pair_advice(hand[0]["rank"], d)
        if advice:
            return advice

    if can_surrender and not soft:
        advice = _surrender_advice(total, d)
        if advice:
            return advice

    if soft:
        action, why = _soft_advice(total, d, can_double)
    else:
        action, why = _hard_advice(total, d, can_double)
    return action, why + " " + _dealer_note(d)


def insurance_advice():
    """Basic strategy always declines insurance."""
    return DECLINE_INSURANCE, (
        "Insurance pays 2 to 1, but the dealer has a 10-value hole card only about 31% of "
        "the time. You'd need 33% to break even, so it loses money long-term. "
        "(Taking it when you hold Blackjack is the same bet, usually called 'even money'.)"
    )

def bet_advice(chips):
    """A simple bankroll-management tip for choosing a bet size."""
    low = max(1, int(chips * 0.01))
    high = max(low, int(chips * 0.05))
    return ("Basic strategy can't predict the next hand, so keep bets steady at about 1-5% of your "
            "bankroll (" + str(low) + "-" + str(high) + " chips right now). Don't raise bets to chase losses.")


class StrategyTracker:
    """Quietly grades every decision against basic strategy"""

    def __init__(self):
        self.total = 0
        self.correct = 0
        self.mistakes = Counter()

    def record(self, situation, chosen, recommended):
        self.total += 1
        if chosen == recommended:
            self.correct += 1
        else:
            self.mistakes[(situation, chosen, recommended)] += 1

    def summary_lines(self):
        if self.total == 0:
            return ["Strategy decisions: none recorded."]

        pct = 100 * self.correct / self.total
        lines = ["Strategy accuracy: " + str(self.correct) + "/" + str(self.total)
                 + " (" + format(pct, ".0f") + "%)"]
        if not self.mistakes:
            lines.append("Perfect basic strategy this session!")
            return lines

        lines.append("Most common mistakes:")
        for (situation, chosen, recommended), count in self.mistakes.most_common(5):
            line = ("  " + situation + ": you chose " + chosen
                    + ", basic strategy says " + recommended)
            if count > 1:
                line += " (x" + str(count) + ")"
            lines.append(line)
        return lines