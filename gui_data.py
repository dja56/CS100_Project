"""gui_state.py - Simple data dictionary for a Blackjack GUI."""

import player
import trainer


def get_gui_state(
    player_hands,
    dealer_hand,
    hide_dealer=True,
    active_hand=0,
    can_hit=True,
    can_stand=True,
    can_double=False,
    can_split=False,
    coach_enabled=False,
    chips=100,
    bet=0,
    stats=None,
    status_text="",
):
    if stats is None:
        stats = {"rounds": 0, "wins": 0, "losses": 0, "pushes": 0}

    formatted_hands = []
    for i, hand in enumerate(player_hands):
        total, soft = player.calculate_hand(hand)
        formatted_hands.append({
            "hand_number": i + 1,
            "is_active": i == active_hand,
            "cards": [player.format_card(c) for c in hand],
            "raw_cards": hand,
            "total": total,
            "soft": soft,
        })

    if hide_dealer and dealer_hand:
        dealer_info = {
            "cards": [player.format_card(dealer_hand[0]), "Hidden card"],
            "raw_cards": dealer_hand[:1],
            "total": None,
            "soft": False,
        }
    else:
        d_total, d_soft = player.calculate_hand(dealer_hand)
        dealer_info = {
            "cards": [player.format_card(c) for c in dealer_hand],
            "raw_cards": dealer_hand,
            "total": d_total,
            "soft": d_soft,
        }

    advice = None
    if coach_enabled and player_hands and dealer_hand:
        advice = trainer.coach_advice(
            player_hands[active_hand],
            dealer_hand[0],
            can_split,
            can_double,
        )

    return {
        "player_hands": formatted_hands,
        "dealer": dealer_info,
        "buttons": {
            "hit": can_hit,
            "stand": can_stand,
            "double": can_double,
            "split": can_split,
        },
        "coach": advice,  # (action, explanation) or None
        "betting": {"chips": chips, "bet": bet},
        "stats": stats,
        "status": status_text,
    }