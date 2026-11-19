import cards
import player
import dealer
import display
import trainer
import betting

# Blackjack Trainer - Terminal Version
# Rules:
# - One standard 52-card deck, shuffled for each round
# - Face cards (J, Q, K) are worth 10; Aces are worth 1 or 11
# - Dealer stands on all 17s, including soft 17
# - You start with 100 chips and bet whole chips before each round
# - Blackjack pays 3 to 2; other wins pay 1 to 1
# - One split is allowed per round
# - Split Aces receive one card each and then stand
# - Player can double down on their first two cards (also after a split)
# - Insurance is offered when the dealer shows an Ace (pays 2 to 1)
# - Late surrender: give up half your bet as your first action on an unsplit hand
# - Coach Mode can be turned on or off (type ? for a hint any time)
# - Every decision is graded against basic strategy in the session summary


def initialize_game():
    """Create a deck and deal two cards to the player and dealer."""
    deck = cards.create_deck()
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = dealer.deal_dealer_hand(deck)
    return deck, player_hand, dealer_hand


def check_winner(player_hand, dealer_hand):
    """Return the result for one player hand."""
    player_total = cards.calculate_hand(player_hand)[0]
    dealer_total = cards.calculate_hand(dealer_hand)[0]

    if player_total > 21:
        return "bust"
    if dealer_total > 21:
        return "win"
    if player_total > dealer_total:
        return "win"
    if player_total < dealer_total:
        return "lose"
    return "push"


def ask_yes_no(prompt):
    while True:
        answer = input(prompt).strip().lower()
        if answer in ["y", "yes"]:
            return True
        if answer in ["n", "no"]:
            return False
        print("Please enter y or n.")


def offer_insurance(cost, coach_enabled, tracker):
    """Offer insurance against a dealer Blackjack. Returns True if taken."""
    print("\nThe dealer is showing an Ace.")
    if coach_enabled:
        advice, why = trainer.insurance_advice()
        print("Coach recommends:", advice)
        print(why)

    took = ask_yes_no("Take insurance for " + betting.fmt(cost) + " chips? (y/n): ")
    tracker.record(
        "Insurance offer",
        trainer.TAKE_INSURANCE if took else trainer.DECLINE_INSURANCE,
        trainer.DECLINE_INSURANCE,
    )
    return took


def play_round(coach_enabled, bankroll, tracker):
    """Run one complete round. Returns (result, net_chips)."""
    if coach_enabled:
        print("\nCoach:", trainer.bet_advice(bankroll.chips))
    bet = betting.prompt_bet(bankroll)

    deck, starting_hand, dealer_hand = initialize_game()

    print("\n==============================")
    print("       BLACKJACK TRAINER")
    print("==============================")
    print("Bet:", betting.fmt(bet), "| Chips:", betting.fmt(bankroll.chips))
    display.display_cards(starting_hand, dealer_hand, hide_dealer=True)

    net = 0
    insurance_bet = 0

    # Insurance (only offered when the dealer shows an Ace).
    if dealer.shows_ace(dealer_hand):
        cost = bet / 2
        if bankroll.chips - bet >= cost:
            if offer_insurance(cost, coach_enabled, tracker):
                insurance_bet = cost
        else:
            print("\nThe dealer is showing an Ace, but you don't have enough chips for insurance.")

    # The dealer checks the hole card when showing a 10-value card or an Ace.
    if dealer.shows_ten_or_ace(dealer_hand):
        print("\nThe dealer checks for Blackjack...")

    player_blackjack = cards.is_blackjack(starting_hand)

    if dealer.has_blackjack(dealer_hand):
        display.display_cards(starting_hand, dealer_hand, hide_dealer=False)
        if insurance_bet:
            net += 2 * insurance_bet
            print("The dealer has Blackjack. Insurance pays 2 to 1:",
                  "+" + betting.fmt(2 * insurance_bet))
        if player_blackjack:
            print("Both you and the dealer have Blackjack. Push!")
            return "push", net
        net -= bet
        print("The dealer has Blackjack. You lose", betting.fmt(bet), "chips.")
        return "lose", net

    if dealer.shows_ten_or_ace(dealer_hand):
        print("The dealer does not have Blackjack.")
    if insurance_bet:
        net -= insurance_bet
        print("Insurance bet lost:", "-" + betting.fmt(insurance_bet))

    if player_blackjack:
        display.display_cards(starting_hand, dealer_hand, hide_dealer=False)
        winnings = bet * 1.5
        net += winnings
        print("Blackjack pays 3 to 2! You win", betting.fmt(winnings), "chips.")
        return "win", net

    hands = [starting_hand]
    bets = [bet]
    hand_number = 1
    split_used = False

    while hand_number <= len(hands):
        available = bankroll.chips - sum(bets) - insurance_bet
        result = player.play_player_hand(
            deck,
            hands[hand_number - 1],
            dealer_hand,
            hand_number,
            coach_enabled,
            bets[hand_number - 1],
            available,
            tracker,
            allow_split=(not split_used and hand_number == 1),
            allow_surrender=not split_used,
        )

        if result == "surrender":
            loss = bets[0] / 2
            net -= loss
            print("\nYou surrender. You lose half your bet:", "-" + betting.fmt(loss))
            return "lose", net

        if result == "split":
            split_used = True
            split_aces = hands[0][0]["rank"] == "A"
            first_hand, second_hand = player.split_hand(deck, hands[0])
            hands = [first_hand, second_hand]
            bets = [bet, bet]

            print("\nYou split your pair into two hands (each bet",
                  betting.fmt(bet) + ").")
            print("Hand 1 received:", cards.format_card(first_hand[-1]))
            print("Hand 2 received:", cards.format_card(second_hand[-1]))

            if split_aces:
                print("Split Aces receive only one card each. Both hands are finished.")
                # Split Aces get one card each and cannot take further actions.
                hand_number = 3
            else:
                hand_number = 1
            continue

        if result == "double":
            bets[hand_number - 1] *= 2
            print("Your bet on this hand is now", betting.fmt(bets[hand_number - 1]) + ".")

        hand_number += 1

    # If the player busted with every hand, the dealer does not need to draw.
    active_hands = [
        hand for hand in hands if cards.calculate_hand(hand)[0] <= 21
    ]

    if active_hands:
        dealer.dealer_turn(deck, dealer_hand)
    else:
        print("\nAll player hands busted. Dealer does not need to draw.")

    if len(hands) == 1:
        display.display_cards(hands[0], dealer_hand, hide_dealer=False)
    else:
        for index, hand in enumerate(hands, start=1):
            display.display_player_hand(hand, index, bets[index - 1])
        display.display_dealer_hand(dealer_hand, hide_dealer=False)
        print("\nFinal results:")

    wins = losses = pushes = 0

    for index, hand in enumerate(hands, start=1):
        hand_bet = bets[index - 1]
        total = cards.calculate_hand(hand)[0]
        outcome = check_winner(hand, dealer_hand)
        if outcome == "win":
            wins += 1
            change = hand_bet
        elif outcome in ["lose", "bust"]:
            losses += 1
            change = -hand_bet
        else:
            pushes += 1
            change = 0
        net += change

        print("Hand", index, "- Total:", total, "-", outcome.upper(),
              "(" + format(change, "+g") + " chips)")

    if wins and not losses and not pushes:
        print("You won every hand!")
    elif losses and not wins and not pushes:
        print("You lost every hand.")
    else:
        print("Round complete:", wins, "win(s),", losses, "loss(es),", pushes, "push(es).")

    if wins > losses:
        return "win", net
    if losses > wins:
        return "lose", net
    return "push", net


def play_again():
    """Ask whether the player wants another round."""
    return ask_yes_no("\nWould you like to play again? (y/n): ")


def main():
    print("Welcome to Blackjack Trainer!")
    print("Practice blackjack with practice chips; no real money involved.")

    coach_mode = input("\nEnable Coach Mode for every hand? (y/n): ").strip().lower() == "y"

    bankroll = betting.Bankroll()
    tracker = trainer.StrategyTracker()

    rounds = 0
    wins = 0
    losses = 0
    pushes = 0

    while True:
        result, net = play_round(coach_mode, bankroll, tracker)
        rounds += 1

        if result == "win":
            wins += 1
        elif result == "lose":
            losses += 1
        else:
            pushes += 1

        bankroll.settle(net)
        print("\nNet this round:", format(net, "+g"), "chips | Chips now:",
              betting.fmt(bankroll.chips))

        if bankroll.is_broke():
            print("You're out of chips!")
            if ask_yes_no("Buy in again for " + str(bankroll.starting) + " chips? (y/n): "):
                bankroll.rebuy()
                continue
            break

        if not play_again():
            break

    print("\n========== SESSION SUMMARY ==========")
    print("Rounds played:", rounds)
    print("Wins:", wins)
    print("Losses:", losses)
    print("Pushes:", pushes)
    print("Final chips:", betting.fmt(bankroll.chips))
    print("Profit/loss:", format(bankroll.profit(), "+g"), "chips",
          "(" + str(bankroll.buy_ins) + " buy-in" + ("s" if bankroll.buy_ins > 1 else "") + ")")
    print()
    for line in tracker.summary_lines():
        print(line)
    print("\nThanks for using Blackjack Trainer!")


if __name__ == "__main__":
    main()