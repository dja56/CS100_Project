"""Pygame interface for Blackjack Trainer. Run with ``python gui.py``."""

try:
    import pygame
except ImportError as exc:
    raise SystemExit("Pygame is required. Install it with: python -m pip install pygame") from exc

import dealer
import main as game
import player
import trainer


WIDTH, HEIGHT = 1000, 700
GREEN = (19, 102, 67)
DARK_GREEN = (12, 66, 47)
GOLD = (242, 194, 76)
WHITE = (248, 247, 239)
RED = (184, 53, 52)
INK = (31, 36, 34)
GRAY = (190, 198, 190)


class BlackjackGUI:
    def __init__(self):
        """Set up the Pygame window, fonts, initial screen, and session totals."""
        pygame.init()
        pygame.display.set_caption("Blackjack Trainer")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("segoeui", 22)
        self.small = pygame.font.SysFont("segoeui", 17)
        self.title = pygame.font.SysFont("segoeui", 36, bold=True)
        self.big = pygame.font.SysFont("segoeui", 28, bold=True)
        self.coach = False
        self.screen_name = "home"
        self.mode = ""
        self.stats = {"rounds": 0, "win": 0, "lose": 0, "push": 0}
        self.message = "Welcome! Choose an action to begin."
        self.advice = ""

    def start_game(self, training):
        """Choose a mode and deal the first round."""
        self.coach = training
        self.mode = "Training Mode" if training else "Regular Mode"
        self.screen_name = "game"
        self.new_round()

    def new_round(self):
        """Deal a fresh round and immediately resolve any natural blackjack."""
        self.deck, hand, self.dealer_hand = game.initialize_game()
        self.hands = [hand]
        self.active = 0
        self.split_used = False
        self.split_aces = False
        self.finished = False
        self.round_result = None
        self.message = "Your turn."
        self.advice = ""
        p_total = player.calculate_hand(hand)[0]
        d_total = player.calculate_hand(self.dealer_hand)[0]
        if len(hand) == 2 and (p_total == 21 or d_total == 21):
            if p_total == d_total:
                self.finish_round("push", "Both have Blackjack. Push!")
            elif p_total == 21:
                self.finish_round("win", "Blackjack! You win!")
            else:
                self.finish_round("lose", "Dealer has Blackjack.")
        self.update_advice()

    def can_split(self):
        """Return whether the active hand is currently eligible to split."""
        return player.can_split(self.hands[self.active], self.active == 0 and not self.split_used,
                                not self.split_used)

    def can_double(self):
        """Return whether the active hand is currently eligible to double down."""
        return player.can_double(self.hands[self.active], len(self.hands[self.active]) == 2
                                 and not (self.split_used and self.active == 0 and self.split_aces))

    def act(self, action):
        """Apply a player action and advance the round when the hand is done."""
        if self.finished:
            if action == "next":
                self.new_round()
            return
        hand = self.hands[self.active]
        total = player.calculate_hand(hand)[0]
        if total >= 21:
            self.advance_hand()
            return
        if action == "hit":
            card = player.hit(self.deck, hand)
            self.message = f"Drew {player.format_card(card)}."
            if player.calculate_hand(hand)[0] >= 21:
                self.advance_hand()
        elif action == "stand":
            self.message = "You stand."
            self.advance_hand()
        elif action == "double" and self.can_double():
            card = player.double_down(self.deck, hand)
            self.message = f"Doubled down and drew {player.format_card(card)}."
            self.advance_hand()
        elif action == "split" and self.can_split():
            self.split_used = True
            self.split_aces = hand[0]["rank"] == "A"
            first, second = player.split_hand(self.deck, hand)
            self.hands = [first, second]
            self.active = 0
            self.message = "Pair split into two hands."
            if self.split_aces:
                self.active = 2
                self.resolve_round()
        self.update_advice()

    def update_advice(self):
        """Refresh coach guidance for the current hand when training is enabled."""
        if not self.coach or self.finished or self.active >= len(self.hands):
            self.advice = ""
            return
        rec, explanation = trainer.coach_advice(self.hands[self.active], self.dealer_hand[0],
                                                self.can_split(), self.can_double())
        self.advice = f"Coach: {rec} — {explanation}"

    def advance_hand(self):
        """Move to the next split hand or resolve the round."""
        self.active += 1
        if self.active >= len(self.hands):
            self.resolve_round()
        elif self.split_aces:
            self.active = len(self.hands)
            self.resolve_round()
        self.update_advice()

    def resolve_round(self):
        """Play the dealer's turn, score every player hand, and finish the round."""
        if any(player.calculate_hand(h)[0] <= 21 for h in self.hands):
            while dealer.dealer_should_hit(self.dealer_hand):
                self.dealer_hand.append(self.deck.pop())
        results = [game.check_winner(hand, self.dealer_hand) for hand in self.hands]
        wins = results.count("win")
        losses = results.count("lose") + results.count("bust")
        if wins > losses:
            result = "win"
        elif losses > wins:
            result = "lose"
        else:
            result = "push"
        message = "   ".join(f"Hand {i + 1}: {r.upper()}" for i, r in enumerate(results))
        self.finish_round(result, message)

    def finish_round(self, result, message):
        """Record the round result and prepare the interface for the next deal."""
        self.finished = True
        self.round_result = result
        self.message = message
        self.stats["rounds"] += 1
        self.stats[result] += 1

    def draw_text(self, text, x, y, color=WHITE, font=None):
        """Render text at a screen position using the requested color and font."""
        surface = (font or self.font).render(text, True, color)
        self.screen.blit(surface, (x, y))

    def draw_card(self, card, x, y, hidden=False):
        """Draw one playing card, showing a card back when it is hidden."""
        rect = pygame.Rect(x, y, 86, 122)
        pygame.draw.rect(self.screen, (28, 36, 34), rect.move(3, 4), border_radius=8)
        pygame.draw.rect(self.screen, DARK_GREEN if hidden else WHITE, rect, border_radius=8)
        if hidden:
            pygame.draw.rect(self.screen, GOLD, rect.inflate(-12, -12), 2, border_radius=5)
            self.draw_text("♠", x + 28, y + 37, GOLD, self.big)
            return
        suit = {"spade": "♠", "club": "♣", "heart": "♥", "diamond": "♦"}[card["suit"]]
        color = RED if card["suit"] in ("heart", "diamond") else INK
        self.draw_text(card["rank"], x + 9, y + 7, color, self.big)
        self.draw_text(suit, x + 29, y + 44, color, self.big)

    def draw_hand(self, hand, y, label, active=False, hide_second=False, x=60,
                  card_pitch=100, total_below=False):
        """Draw a hand, its label, and its visible blackjack total."""
        self.draw_text(label + ("  •  YOUR TURN" if active else ""), x, y - 35,
                       GOLD if active else WHITE, self.font)
        for i, card in enumerate(hand):
            self.draw_card(card, x + i * card_pitch, y, hide_second and i == 1)
        total = player.calculate_hand(hand)[0]
        total_text = f"Total: {total if not hide_second else player.calculate_hand([hand[0]])[0]}"
        total_x = x if total_below else x + len(hand) * card_pitch + 14
        total_y = y + 126 if total_below else y + 43
        self.draw_text(total_text, total_x, total_y, GOLD, self.font)

    def draw_button(self, text, rect, enabled=True, key=""):
        """Draw a button and visually distinguish enabled from disabled actions."""
        color = (218, 168, 58) if enabled else (91, 107, 99)
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 226, 148) if enabled else GRAY, rect, 2, border_radius=10)
        label = text + (f"  [{key}]" if key else "")
        surf = self.font.render(label, True, INK if enabled else (220, 224, 218))
        self.screen.blit(surf, surf.get_rect(center=rect.center))

    def draw(self):
        """Render the current home, mode selection, or blackjack table screen."""
        if self.screen_name == "home":
            self.draw_home()
            pygame.display.flip()
            return
        if self.screen_name == "mode":
            self.draw_mode_select()
            pygame.display.flip()
            return
        self.screen.fill(GREEN)
        pygame.draw.rect(self.screen, DARK_GREEN, (0, 0, WIDTH, 76))
        self.draw_text("BLACKJACK TRAINER", 35, 18, GOLD, self.title)
        self.draw_text(self.mode, 600, 28, GOLD, self.small)
        self.draw_text(f"Rounds  {self.stats['rounds']}   W {self.stats['win']}   L {self.stats['lose']}   P {self.stats['push']}",
                       600, 51, WHITE, self.small)
        self.draw_hand(self.dealer_hand, 138, "DEALER", hide_second=not self.finished)
        if len(self.hands) == 2:
            # Put split hands in separate table columns so their cards never cover each other.
            self.draw_hand(self.hands[0], 350, "Hand 1", active=not self.finished and self.active == 0,
                           x=48, card_pitch=72, total_below=True)
            self.draw_hand(self.hands[1], 350, "Hand 2", active=not self.finished and self.active == 1,
                           x=510, card_pitch=72, total_below=True)
        else:
            self.draw_hand(self.hands[0], 355, "Hand 1",
                           active=not self.finished and self.active == 0)
        pygame.draw.line(self.screen, (78, 143, 108), (40, 515), (960, 515), 2)
        self.draw_text(self.message, 48, 528, GOLD, self.font)
        if self.coach and not self.finished:
            pygame.draw.rect(self.screen, DARK_GREEN, (40, 555, 920, 55), border_radius=8)
            self.draw_text("COACH", 54, 563, GOLD, self.small)
            self.draw_text(self.advice, 125, 563, WHITE, self.small)
        self.draw_button("Hit", pygame.Rect(48, 625, 170, 52), not self.finished, "H")
        self.draw_button("Stand", pygame.Rect(238, 625, 170, 52), not self.finished, "S")
        self.draw_button("Double", pygame.Rect(428, 625, 170, 52), not self.finished and self.can_double(), "D")
        if not self.finished and self.can_split():
            self.draw_button("Split", pygame.Rect(618, 625, 170, 52), True, "P")
        if self.finished:
            self.draw_button("Next Round", pygame.Rect(618, 625, 170, 52), True, "N")
        self.draw_button("Exit", pygame.Rect(808, 625, 170, 52), True)
        pygame.display.flip()

    def draw_home(self):
        """Render the title screen and its Start button."""
        self.screen.fill(DARK_GREEN)
        pygame.draw.ellipse(self.screen, GREEN, (-180, 270, 800, 760))
        pygame.draw.ellipse(self.screen, (22, 91, 62), (480, -350, 800, 800))
        self.draw_text("BLACKJACK", 90, 180, GOLD, self.title)
        self.draw_text("TRAINER", 90, 228, WHITE, self.title)
        self.draw_text("Practice your strategy, one hand at a time.", 94, 292, GRAY, self.font)
        # Decorative cards
        self.draw_card({"rank": "A", "suit": "spade"}, 650, 176)
        self.draw_card({"rank": "K", "suit": "heart"}, 720, 198)
        self.draw_button("START", pygame.Rect(94, 390, 250, 66), True)
        self.draw_text("Click Start to choose a game mode", 95, 475, GRAY, self.small)

    def draw_mode_select(self):
        """Render the Training Mode and Regular Mode choices."""
        self.screen.fill(GREEN)
        pygame.draw.rect(self.screen, DARK_GREEN, (0, 0, WIDTH, 90))
        self.draw_text("CHOOSE YOUR MODE", 50, 23, GOLD, self.title)
        self.draw_text("Select how you want to play.", 50, 160, WHITE, self.font)
        pygame.draw.rect(self.screen, DARK_GREEN, (80, 235, 390, 250), border_radius=18)
        pygame.draw.rect(self.screen, DARK_GREEN, (530, 235, 390, 250), border_radius=18)
        self.draw_text("TRAINING MODE", 120, 275, GOLD, self.big)
        self.draw_text("Coach advice stays on", 120, 327, WHITE, self.font)
        self.draw_text("throughout the game.", 120, 358, WHITE, self.font)
        self.draw_text("REGULAR MODE", 570, 275, GOLD, self.big)
        self.draw_text("Play without coach", 570, 327, WHITE, self.font)
        self.draw_text("recommendations.", 570, 358, WHITE, self.font)
        self.draw_button("Start Training", pygame.Rect(120, 410, 300, 54), True)
        self.draw_button("Start Regular", pygame.Rect(570, 410, 300, 54), True)
        self.draw_text("← Back", 50, 625, GRAY, self.small)

    def run(self):
        """Handle input and redraw the application until the window closes."""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if self.screen_name == "home" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.screen_name = "mode"
                        continue
                    if self.screen_name == "mode" and event.key == pygame.K_ESCAPE:
                        self.screen_name = "home"
                        continue
                    if self.screen_name == "game" and event.key == pygame.K_ESCAPE:
                        self.screen_name = "mode"
                        continue
                    if self.screen_name != "game":
                        continue
                    key_actions = {pygame.K_h: "hit", pygame.K_s: "stand",
                                   pygame.K_d: "double", pygame.K_p: "split"}
                    if event.key in key_actions:
                        self.act(key_actions[event.key])
                    elif event.key == pygame.K_n and self.finished:
                        self.new_round()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = event.pos
                    if self.screen_name == "home":
                        if pygame.Rect(94, 390, 250, 66).collidepoint(event.pos):
                            self.screen_name = "mode"
                    elif self.screen_name == "mode":
                        if pygame.Rect(120, 410, 300, 54).collidepoint(event.pos):
                            self.start_game(training=True)
                        elif pygame.Rect(570, 410, 300, 54).collidepoint(event.pos):
                            self.start_game(training=False)
                        elif y >= 600 and x <= 150:
                            self.screen_name = "home"
                    else:
                        buttons = [(pygame.Rect(48, 625, 170, 52), "hit"),
                                   (pygame.Rect(238, 625, 170, 52), "stand"),
                                   (pygame.Rect(428, 625, 170, 52), "double")]
                        if not self.finished and self.can_split():
                            buttons.append((pygame.Rect(618, 625, 170, 52), "split"))
                        if self.finished:
                            buttons.append((pygame.Rect(618, 625, 170, 52), "next"))
                        buttons.append((pygame.Rect(808, 625, 170, 52), "back"))
                        for rect, action in buttons:
                            if rect.collidepoint(event.pos):
                                if action == "back":
                                    self.screen_name = "mode"
                                else:
                                    self.act(action)
                                break
            self.draw()
            self.clock.tick(60)


if __name__ == "__main__":
    BlackjackGUI().run()
