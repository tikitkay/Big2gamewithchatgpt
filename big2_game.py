import pygame
import random
import os

# Pygame 초기화
pygame.init()

# 화면 설정
screen_width = 1200
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Big 2 Game")

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 128, 0)  # 카지노 배경색

# 효과음 로드
pygame.mixer.init()
play_sound = pygame.mixer.Sound(os.path.join('sounds', 'play_card.mp3'))
pass_sound = pygame.mixer.Sound(os.path.join('sounds', 'pass.mp3'))

# 카드 클래스 정의
class Card:
    order = {'3': 0, '4': 1, '5': 2, '6': 3, '7': 4, '8': 5, '9': 6, '0': 7, 'J': 8, 'Q': 9, 'K': 10, 'A': 11, '2': 12}
    suits_order = {'diamonds': 0, 'clubs': 1, 'hearts': 2, 'spades': 3}

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        suit_abbr = suit[0].lower()  # 'diamonds' -> 'd', 'clubs' -> 'c', etc.
        image_path = os.path.join('cards', f'{rank}_of_{suit_abbr}.png')
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.selected = False
        self.back_image = pygame.image.load(os.path.join('cards', 'back.png'))

    def __repr__(self):
        return f"{self.rank} of {self.suit}"

    def __lt__(self, other):
        if Card.order[self.rank] == Card.order[other.rank]:
            return Card.suits_order[self.suit] < Card.suits_order[other.suit]
        return Card.order[self.rank] < Card.order[other.rank]

    def __gt__(self, other):
        if Card.order[self.rank] == Card.order[other.rank]:
            return Card.suits_order[self.suit] > Card.suits_order[other.suit]
        return Card.order[self.rank] > Card.order[other.rank]

    def draw(self, screen, scale=1.0, face_up=True):
        if face_up:
            image = pygame.transform.scale(self.image, (int(self.rect.width * scale), int(self.rect.height * scale)))
        else:
            image = pygame.transform.scale(self.back_image, (int(self.rect.width * scale), int(self.rect.height * scale)))
        rect = image.get_rect(topleft=self.rect.topleft)
        if self.selected and face_up:
            pygame.draw.rect(screen, BLUE, rect.inflate(10, 10), 3)  # 카드 선택 표시
        screen.blit(image, rect)

# 덱 클래스 정의
class Deck:
    suits = ['diamonds', 'clubs', 'hearts', 'spades']
    ranks = ['3', '4', '5', '6', '7', '8', '9', '0', 'J', 'Q', 'K', 'A', '2']

    def __init__(self):
        self.cards = [Card(suit, rank) for suit in self.suits for rank in self.ranks]
        random.shuffle(self.cards)

    def deal(self, num_players):
        return [self.cards[i::num_players] for i in range(num_players)]

# 게임 클래스 정의
class Big2Game:
    def __init__(self):
        self.deck = Deck()
        self.hands = self.deck.deal(4)  # 4명의 플레이어
        for hand in self.hands:
            hand.sort()
        self.current_player = 0
        self.previous_play = []
        self.last_played_player = None
        self.starting_player = self.find_starting_player()
        self.winner = None
        self.passes = [False] * 4  # 각 플레이어의 패스 상태를 저장
        self.game_started = False
        self.new_round = False  # 새로운 라운드 시작 여부

    def find_starting_player(self):
        for i, hand in enumerate(self.hands):
            for card in hand:
                if card.rank == '3' and card.suit == 'diamonds':
                    return i
        return 0

    def start_game(self):
        self.__init__()  # 게임을 재시작할 때 초기화
        self.current_player = self.starting_player
        self.game_started = True
        print(f"Game started. Player {self.current_player + 1} starts.")

    def next_turn(self):
        self.current_player = (self.current_player + 1) % 4
        while self.passes[self.current_player]:
            self.current_player = (self.current_player + 1) % 4
        print(f"Player {self.current_player + 1}'s turn.")

    def draw(self, screen):
        # 첫 번째 플레이어의 카드는 맨 마지막에 그립니다.
        for player_num, hand in enumerate(self.hands):
            if player_num == 0:
                continue  # 첫 번째 플레이어의 카드는 건너뜁니다.

            face_up = False  # AI 플레이어의 카드는 뒷면으로 표시

            if player_num == 1:  # 왼쪽에 배치
                for i, card in enumerate(hand):
                    card.rect.topleft = (10, screen_height // 2 - len(hand) * 15 + i * 30)
                    card.draw(screen, scale=0.6, face_up=face_up)
            elif player_num == 2:  # 상단에 배치
                for i, card in enumerate(hand):
                    card.rect.topleft = (screen_width // 2 - len(hand) * 25 + i * 50, 10)
                    card.draw(screen, scale=0.6, face_up=face_up)
            elif player_num == 3:  # 오른쪽에 배치
                for i, card in enumerate(hand):
                    card.rect.topleft = (screen_width - 70, screen_height // 2 - len(hand) * 15 + i * 30)
                    card.draw(screen, scale=0.6, face_up=face_up)

        # 첫 번째 플레이어의 카드 그리기
        for i, card in enumerate(self.hands[0]):
            card.rect.topleft = (i * 70 + 50, screen_height - 150)
            card.draw(screen)

        # 중앙에 이전 플레이된 카드 그리기
        for i, card in enumerate(self.previous_play):
            card.rect.topleft = (screen_width // 2 - 35 + i * 40, screen_height // 2 - 75)
            card.draw(screen)

        # 중앙에 현재 턴 표시
        font = pygame.font.Font(None, 36)
        if self.winner:
            text = font.render(f"Player {self.winner} wins!", True, BLACK)
        else:
            text = font.render(f"Player {self.current_player + 1}'s turn", True, BLACK)
        rect = text.get_rect(center=(screen_width // 2, screen_height // 2 - 150))
        screen.blit(text, rect)

        # 조작키 안내 표시
        instructions = [
            "Controls:",
            "SPACE: Play selected cards",
            "P: Pass turn",
            "Suits: D < C < H < S"
        ]
        instruction_font = pygame.font.Font(None, 24)
        for i, line in enumerate(instructions):
            instruction_text = instruction_font.render(line, True, BLACK)
            screen.blit(instruction_text, (20, 20 + i * 30))

        if not self.game_started:
            self.draw_start_button(screen)
        if self.winner:
            self.draw_end_buttons(screen)

    def draw_start_button(self, screen):
        font = pygame.font.Font(None, 74)
        text = font.render("Start Game", True, WHITE)
        rect = text.get_rect(center=(screen_width // 2, screen_height // 2))
        pygame.draw.rect(screen, RED, rect.inflate(20, 20))
        screen.blit(text, rect)
        return rect

    def draw_end_buttons(self, screen):
        font = pygame.font.Font(None, 50)
        restart_text = font.render("Restart Game", True, WHITE)
        quit_text = font.render("Quit Game", True, WHITE)
        restart_rect = restart_text.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
        quit_rect = quit_text.get_rect(center=(screen_width // 2, screen_height // 2 + 150))
        pygame.draw.rect(screen, RED, restart_rect.inflate(20, 20))
        pygame.draw.rect(screen, RED, quit_rect.inflate(20, 20))
        screen.blit(restart_text, restart_rect)
        screen.blit(quit_text, quit_rect)
        return restart_rect, quit_rect

    def handle_click(self, pos):
        if not self.game_started:
            start_button_rect = self.draw_start_button(screen)
            if start_button_rect.collidepoint(pos):
                self.start_game()
        elif self.winner:
            restart_rect, quit_rect = self.draw_end_buttons(screen)
            if restart_rect.collidepoint(pos):
                self.start_game()
            elif quit_rect.collidepoint(pos):
                pygame.quit()
                exit()
        else:
            if self.current_player == 0:  # 첫 번째 플레이어가 클릭할 수 있도록
                for card in reversed(self.hands[0]):
                    if card.rect.collidepoint(pos):
                        card.selected = not card.selected
                        print(f"Card {card} selected: {card.selected}")
                        break

    def play_cards(self):
        selected_cards = [card for card in self.hands[self.current_player] if card.selected]
        selected_cards.sort(key=lambda card: (Card.order[card.rank], Card.suits_order[card.suit]))
        print(f"Player {self.current_player + 1} selected cards: {selected_cards}")
        if self.is_valid_play(selected_cards):
            for card in selected_cards:
                self.hands[self.current_player].remove(card)
            if self.new_round:
                self.previous_play = []
                self.new_round = False
            self.previous_play = selected_cards
            self.last_played_player = self.current_player  # 마지막으로 카드를 낸 플레이어 업데이트
            self.passes = [False] * 4  # 모든 플레이어의 패스 상태 초기화
            print(f"Player {self.current_player + 1} played cards: {selected_cards}")
            for i, card in enumerate(selected_cards):  # 중앙으로 이동
                card.rect.topleft = (screen_width // 2 - 35 + i * 40, screen_height // 2 - 75)
            play_sound.play()  # 카드 내기 효과음
            screen.fill(GREEN)  # 배경을 초록색으로 설정
            self.draw(screen)  # 카드 그리기
            pygame.display.flip()  # 렉 문제 해결을 위해 추가
            pygame.time.wait(2000)  # 중앙으로 이동 후 딜레이 추가
            if not self.hands[self.current_player]:
                self.winner = self.current_player + 1
                print(f"Player {self.winner} wins!")
            else:
                self.next_turn()
        else:
            print("Invalid play.")
            for card in selected_cards:
                card.selected = False  # 선택 해제

    def pass_turn(self):
        self.passes[self.current_player] = True
        print(f"Player {self.current_player + 1} passed.")
        pass_sound.play()  # 패스 효과음
        screen.fill(GREEN)  # 배경을 초록색으로 설정
        self.draw(screen)  # 카드 그리기
        pygame.display.flip()  # 렉 문제 해결을 위해 추가
        pygame.time.wait(2000)  # 패스 후 딜레이 추가
        if self.last_played_player is not None and all(self.passes[i] for i in range(4) if i != self.last_played_player):
            print(f"All other players passed. Player {self.last_played_player + 1} can play any card.")
            self.passes = [False] * 4
            self.previous_play = []
            self.current_player = self.last_played_player
            self.new_round = True
        else:
            self.next_turn()

    def is_valid_play(self, selected_cards):
        if not selected_cards:
            return False
        selected_cards.sort(key=lambda card: (Card.order[card.rank], Card.suits_order[card.suit]))
        # 첫 번째 턴은 다이아몬드 3을 포함해야 함
        if not self.previous_play and not self.new_round:
            if not any(card.rank == '3' and card.suit == 'diamonds' for card in selected_cards):
                return False
            if not (len(selected_cards) == 1 or
                    (len(selected_cards) == 2 and selected_cards[0].rank == selected_cards[1].rank) or
                    (len(selected_cards) == 3 and all(card.rank == selected_cards[0].rank for card in selected_cards)) or
                    (len(selected_cards) == 5 and (self.is_straight(selected_cards) or self.is_full_house(selected_cards) or self.is_flush(selected_cards) or self.is_four_of_a_kind(selected_cards) or self.is_straight_flush(selected_cards)))):
                return False
        # 모든 플레이어가 패스한 경우 새로운 카드를 낼 수 있음
        if self.new_round:
            if not (len(selected_cards) == 1 or
                    (len(selected_cards) == 2 and selected_cards[0].rank == selected_cards[1].rank) or
                    (len(selected_cards) == 3 and all(card.rank == selected_cards[0].rank for card in selected_cards)) or
                    (len(selected_cards) == 5 and (self.is_straight(selected_cards) or self.is_full_house(selected_cards) or self.is_flush(selected_cards) or self.is_four_of_a_kind(selected_cards) or self.is_straight_flush(selected_cards)))):
                return False
            return True
        # 같은 장수의 카드만 플레이할 수 있음
        if self.previous_play and len(selected_cards) != len(self.previous_play):
            return False
        # 단일 카드 플레이
        if len(selected_cards) == 1:
            return not self.previous_play or selected_cards[0] > self.previous_play[0]
        # 페어 플레이
        if len(selected_cards) == 2 and selected_cards[0].rank == selected_cards[1].rank:
            return not self.previous_play or selected_cards[0] > self.previous_play[0]
        # 트리플 플레이 (3장으로만 내야 함)
        if len(selected_cards) == 3 and all(card.rank == selected_cards[0].rank for card in selected_cards):
            return not self.previous_play or (self.previous_play and len(self.previous_play) == 3 and selected_cards[0] > self.previous_play[0])
        # 스트레이트 플레이 (5장)
        if len(selected_cards) == 5 and self.is_straight(selected_cards):
            return not self.previous_play or (self.get_hand_rank(selected_cards) > self.get_hand_rank(self.previous_play))
        # 풀 하우스 플레이 (5장)
        if len(selected_cards) == 5 and self.is_full_house(selected_cards):
            return not self.previous_play or (self.is_full_house(self.previous_play) and self.get_full_house_rank(selected_cards) > self.get_full_house_rank(self.previous_play))
        # 플러쉬 플레이 (5장)
        if len(selected_cards) == 5 and self.is_flush(selected_cards):
            return not self.previous_play or (self.get_hand_rank(selected_cards) > self.get_hand_rank(self.previous_play))
        # 포카드 플레이 (5장)
        if len(selected_cards) == 5 and self.is_four_of_a_kind(selected_cards):
            return not self.previous_play or (self.is_four_of_a_kind(self.previous_play) and self.get_four_of_a_kind_rank(selected_cards) > self.get_four_of_a_kind_rank(self.previous_play))
        # 스트레이트 플러쉬 플레이 (5장)
        if len(selected_cards) == 5 and self.is_straight_flush(selected_cards):
            return not self.previous_play or (self.get_hand_rank(selected_cards) > self.get_hand_rank(self.previous_play))
        return False

    def get_hand_rank(self, cards):
        if self.is_straight_flush(cards):
            return 5
        elif self.is_four_of_a_kind(cards):
            return 4
        elif self.is_full_house(cards):
            return 3
        elif self.is_flush(cards):
            return 2
        elif self.is_straight(cards):
            return 1
        return 0

    def get_full_house_rank(self, cards):
        ranks = [card.rank for card in cards]
        three_of_a_kind_rank = ranks[0] if ranks.count(ranks[0]) == 3 else ranks[2]
        return Card.order[three_of_a_kind_rank]

    def get_four_of_a_kind_rank(self, cards):
        ranks = [card.rank for card in cards]
        return Card.order[ranks[2]]  # 포카드의 중앙 카드의 랭크를 반환

    def is_straight(self, cards):
        cards.sort(key=lambda card: Card.order[card.rank])
        for i in range(len(cards) - 1):
            if Card.order[cards[i].rank] + 1 != Card.order[cards[i + 1].rank]:
                return False
        return True

    def is_full_house(self, cards):
        cards.sort()
        ranks = [card.rank for card in cards]
        return (ranks.count(ranks[0]) == 3 and ranks.count(ranks[3]) == 2) or (ranks.count(ranks[0]) == 2 and ranks.count(ranks[2]) == 3)

    def is_flush(self, cards):
        suits = [card.suit for card in cards]
        return len(set(suits)) == 1

    def is_four_of_a_kind(self, cards):
        cards.sort()
        ranks = [card.rank for card in cards]
        return (ranks.count(ranks[0]) == 4 or ranks.count(ranks[1]) == 4) and len(cards) == 5

    def is_straight_flush(self, cards):
        return self.is_straight(cards) and self.is_flush(cards)

    def automatic_play(self):
        if self.current_player != 0 and self.game_started and not self.winner:  # AI 플레이어
            valid_plays = []

            # 가능한 모든 카드 조합을 탐색
            for size in range(1, 6):
                for i in range(len(self.hands[self.current_player]) - size + 1):
                    selected_cards = self.hands[self.current_player][i:i + size]
                    if self.is_valid_play(selected_cards):
                        valid_plays.append(selected_cards)

            if valid_plays:
                # 2와 A를 마지막에 내도록 조정
                non_high_plays = [play for play in valid_plays if not any(card.rank in ('2', 'A') for card in play)]
                high_plays = [play for play in valid_plays if any(card.rank in ('2', 'A') for card in play)]
                valid_plays = non_high_plays + high_plays

                # 가장 많은 장수의 카드를 우선으로 선택
                valid_plays.sort(key=lambda play: (-len(play), play))
                best_play = valid_plays[0]
                
                for card in best_play:
                    card.selected = True
                self.play_cards()
            else:
                self.pass_turn()  # 낼 카드가 없으면 패스

# 게임 객체 생성
game = Big2Game()

# 메인 루프
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            game.handle_click(event.pos)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game.current_player == 0 and game.game_started and not game.winner:  # 플레이어 1의 턴일 때만
                    game.play_cards()  # 스페이스바를 누르면 선택한 카드를 플레이
            elif event.key == pygame.K_p:  # 'p' 키를 누르면 패스
                if game.current_player == 0 and game.game_started and not game.winner:  # 플레이어 1의 턴일 때만
                    game.pass_turn()

    if game.winner is None and game.game_started:
        game.automatic_play()  # AI 플레이어 자동 턴 진행

    screen.fill(GREEN)  # 배경을 초록색으로 설정
    game.draw(screen)  # 카드 그리기
    pygame.display.flip()

pygame.quit()
