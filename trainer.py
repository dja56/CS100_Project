"""Trainer: beginner-friendly basic-strategy recommendations and explanations."""

from player import calculate_hand, card_value


def coach_advice(hand, dealer_up_card, can_split, can_double):
    """Give beginner-friendly basic-strategy guidance.

    This is an instructional approximation, not a complete casino strategy chart.
    Returns (action, explanation).
    """
    total, soft = calculate_hand(hand)
    dealer_value = min(card_value(dealer_up_card), 10)
    dealer_rank = dealer_up_card["rank"]

    if len(hand) == 2 and can_split and hand[0]["rank"] == hand[1]["rank"]:
        rank = hand[0]["rank"]
        if rank in ["A", "8"]:
            return "SPLIT", "Aces and 8s are generally split in basic strategy."
        if rank in ["10", "J", "Q", "K"]:
            return "STAND", "A pair worth 20 is already a very strong hand. Do not split it."
        if rank == "9" and dealer_value not in [7, 10] and dealer_rank != "A":
            return "SPLIT", "A pair of 9s is often split against weaker dealer cards."
        if rank in ["2", "3", "7"] and dealer_value <= 7:
            return "SPLIT", "This pair can be improved by splitting against a weaker dealer card."
        if rank == "6" and dealer_value <= 6:
            return "SPLIT", "A pair of 6s is commonly split against a dealer 2 through 6."

    if soft:
        if total >= 19:
            return "STAND", "Your soft total is already strong."
        if total == 18:
            if dealer_value in [9, 10, 11]:
                return "HIT", "Soft 18 can lose to strong dealer cards, so hitting is often better."
            if dealer_value in [3, 4, 5, 6] and can_double:
                return "DOUBLE", "Soft 18 can be doubled against a weaker dealer card."
            return "STAND", "Soft 18 is usually good enough against this dealer card."
        if total in [17, 16, 15, 14, 13] and dealer_value in [4, 5, 6] and can_double:
            return "DOUBLE", "A soft hand can take one extra card while keeping some flexibility."
        return "HIT", "Your soft total is low enough that taking another card is usually best."

    if total >= 17:
        return "STAND", "A hard 17 or higher is normally a stand."
    if total >= 13 and dealer_value <= 6:
        return "STAND", "The dealer has a weaker up-card. Let the dealer take the risk of busting."
    if total == 12 and dealer_value in [4, 5, 6]:
        return "STAND", "A hard 12 is commonly stood on against dealer 4, 5, or 6."
    if total in [9, 10, 11] and can_double:
        if total == 11 or (total == 10 and dealer_value <= 9) or (total == 9 and 3 <= dealer_value <= 6):
            return "DOUBLE", "This is a favorable total for doubling against the dealer's up-card."
    return "HIT", "Your total is low, or the dealer's up-card is strong. Taking another card is usually best."