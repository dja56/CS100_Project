import random
import player
import dealer
import trainer

# Blackjack Trainer - Terminal Version
# Rules:
# - One standard 52-card deck, shuffled for each round
# - Face cards (J, Q, K) are worth 10; Aces are worth 1 or 11
# - Dealer stands on all 17s, including soft 17
# - Blackjack pays as a win (there is no real money)
# - One split is allowed per round
# - Split Aces receive one card each and then stand
# - Player can double down on their first two cards
# - Coach Mode can be turned on or off

# TO DO
# Surrender and Insurance


ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10",
         "J", "Q", "K", "A"]
suits = ["spade", "club", "heart", "diamond"]


def create_deck():
    """Create and shuffle a standard deck of 52 cards."""
    deck = []
    for suit in suits:
        for rank in ranks:
            deck.append({"rank": rank, "suit": suit})

    random.shuffle(deck)
    return deck


def initialize_game():
    """Create a deck and deal two cards to the player and dealer."""
    deck = create_deck()
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = dealer.deal_dealer_hand(deck)
    return deck, player_hand, dealer_hand


def display_cards(player_hand, dealer_hand, hide_dealer=True, hand_number=None):
    """Display the player's hand and the dealer's hand."""
    if hand_number is not None:
        print("\n--- Player Hand", hand_number, "---")

    print("Your cards:")
    for card in player_hand:
        print("  " + player.format_card(card))

    total, soft = player.calculate_hand(player_hand)
    hand_type = " (soft)" if soft else ""
    print("Your total:", str(total) + hand_type)

    print("\nDealer's cards:")
    if hide_dealer:
        print("  " + player.format_card(dealer_hand[0]))
        print("  [Hidden card]")
    else:
        for card in dealer_hand:
            print("  " + player.format_card(card))
        dealer_total, dealer_soft = player.calculate_hand(dealer_hand)
        dealer_type = " (soft)" if dealer_soft else ""
        print("Dealer total:", str(dealer_total) + dealer_type)


def check_winner(player_hand, dealer_hand):
    """Return the result for one player hand."""
    player_total = player.calculate_hand(player_hand)[0]
    dealer_total = player.calculate_hand(dealer_hand)[0]

    if player_total > 21:
        return "bust"
    if dealer_total > 21:
        return "win"
    if player_total > dealer_total:
        return "win"
    if player_total < dealer_total:
        return "lose"
    return "push"


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


def play_player_hand(deck, hand, dealer_hand, hand_number, coach_enabled,
                     allow_split=True, split_aces=False):
    """Play one hand. Returns "split" if the player splits, otherwise whether it was doubled."""
    first_action = True

    while True:
        display_cards(hand, dealer_hand, hide_dealer=True, hand_number=hand_number)
        total = player.calculate_hand(hand)[0]

        if total >= 21:
            if total == 21:
                print("You have 21.")
            else:
                print("You busted!")
            return False

        if split_aces:
            print("Split Aces receive only one card. This hand is finished.")
            return False

        split_ok = player.can_split(hand, first_action, allow_split)
        double_ok = player.can_double(hand, first_action)

        if coach_enabled:
            recommendation, explanation = trainer.coach_advice(
                hand, dealer_hand[0], split_ok, double_ok
            )
            print("\nCoach recommends:", recommendation)
            print(explanation)

        action = get_player_action(split_ok, double_ok)

        if action == "H":
            new_card = player.hit(deck, hand)
            print("You drew:", player.format_card(new_card))
        elif action == "S":
            print("You stand.")
            return False
        elif action == "D":
            new_card = player.double_down(deck, hand)
            print("You doubled down and drew:", player.format_card(new_card))
            return True
        elif action == "P":
            # The caller handles the second hand created by a split.
            return "split"

        first_action = False


def play_round(coach_enabled):
    """Run one complete round, including optional splitting."""
    deck, starting_hand, dealer_hand = initialize_game()

    print("\n==============================")
    print("       BLACKJACK TRAINER")
    print("==============================")
    display_cards(starting_hand, dealer_hand, hide_dealer=True)

    player_total = player.calculate_hand(starting_hand)[0]
    dealer_total = player.calculate_hand(dealer_hand)[0]

    player_blackjack = len(starting_hand) == 2 and player_total == 21
    dealer_blackjack = len(dealer_hand) == 2 and dealer_total == 21

    if player_blackjack or dealer_blackjack:
        display_cards(starting_hand, dealer_hand, hide_dealer=False)
        if player_blackjack and dealer_blackjack:
            print("Both you and the dealer have Blackjack. Push!")
            return "push"
        if player_blackjack:
            print("Blackjack! You win!")
            return "win"
        print("The dealer has Blackjack. You lose.")
        return "lose"

    hands = [starting_hand]
    hand_number = 1
    split_used = False

    while hand_number <= len(hands):
        result = play_player_hand(
            deck,
            hands[hand_number - 1],
            dealer_hand,
            hand_number,
            coach_enabled,
            allow_split=(not split_used and hand_number == 1)
        )

        if result == "split":
            split_used = True
            split_aces = hands[0][0]["rank"] == "A"
            first_hand, second_hand = player.split_hand(deck, hands[0])
            hands = [first_hand, second_hand]

            print("\nYou split your pair into two hands.")
            print("Hand 1 received:", player.format_card(first_hand[-1]))
            print("Hand 2 received:", player.format_card(second_hand[-1]))

            if split_aces:
                # Split Aces get one card each and cannot take further actions.
                hand_number = 3
            else:
                hand_number = 1
            continue

        hand_number += 1

    # If the player busted with every hand, the dealer does not need to draw.
    active_hands = [
        hand for hand in hands if player.calculate_hand(hand)[0] <= 21
    ]

    if active_hands:
        dealer.dealer_turn(deck, dealer_hand)
    else:
        print("\nAll player hands busted. Dealer does not need to draw.")

    display_cards(hands[0], dealer_hand, hide_dealer=False)
    if len(hands) > 1:
        print("\nFinal results:")
    wins = losses = pushes = 0

    for index, hand in enumerate(hands, start=1):
        total = player.calculate_hand(hand)[0]
        result = check_winner(hand, dealer_hand)
        if result == "win":
            wins += 1
        elif result in ["lose", "bust"]:
            losses += 1
        else:
            pushes += 1

        print("Hand", index, "- Total:", total, "-", result.upper())

    if wins and not losses and not pushes:
        print("You won every hand!")
    elif losses and not wins and not pushes:
        print("You lost every hand.")
    else:
        print("Round complete:", wins, "win(s),", losses, "loss(es),", pushes, "push(es).")

    if wins > losses:
        return "win"
    if losses > wins:
        return "lose"
    return "push"


def play_again():
    """Ask whether the player wants another round."""
    while True:
        answer = input("\nWould you like to play again? (y/n): ").strip().lower()
        if answer in ["y", "yes"]:
            return True
        if answer in ["n", "no"]:
            return False
        print("Please enter y or n.")


def main():
    print("Welcome to Blackjack Trainer!")
    print("Practice blackjack with no real money involved.")

    coach_mode = input("\nEnable Coach Mode for every hand? (y/n): ").strip().lower() == "y"

    rounds = 0
    wins = 0
    losses = 0
    pushes = 0

    while True:
        result = play_round(coach_mode)
        rounds += 1

        if result == "win":
            wins += 1
        elif result == "lose":
            losses += 1
        else:
            pushes += 1

        if not play_again():
            break

    print("\n========== SESSION SUMMARY ==========")
    print("Rounds played:", rounds)
    print("Wins:", wins)
    print("Losses:", losses)
    print("Pushes:", pushes)
    print("Thanks for using Blackjack Trainer!")


if __name__ == "__main__":
    main()