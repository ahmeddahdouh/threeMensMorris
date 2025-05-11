import pygame
import sys
import time
from ai import ThreeMensMorrisAI
from ai_astar import ThreeMensMorrisAStar

# Initialisation de Pygame
pygame.init()

# Constantes
WIDTH, HEIGHT = 1000, 700  # Increased width to accommodate sidebar
LINE_WIDTH = 5
BOARD_ROWS, BOARD_COLS = 3, 3
CELL_SIZE = 150  # Adjusted for new layout
PION_RADIUS = CELL_SIZE // 3

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BG_COLOR = (220, 220, 220)
LINE_COLOR = (0, 0, 0)
HIGHLIGHT_COLOR = (255, 255, 0)
SIDEBAR_COLOR = (200, 200, 190)
BUTTON_COLOR = (100, 180, 100)
BUTTON_HOVER_COLOR = (120, 200, 120)
BUTTON_TEXT_COLOR = (255, 255, 255)

# Création de la fenêtre
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Three Men's Morris - Fixed Start")
screen.fill(BG_COLOR)

# Police
FONT = pygame.font.Font(None, 36)

class Button:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hover = False

    def draw(self):
        color = BUTTON_HOVER_COLOR if self.hover else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (50, 50, 50), self.rect, 2, border_radius=8)

        text_surf = FONT.render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.action()
                return True
        return False

class Game:
    def __init__(self):
        # Plateau de jeu: 0 = vide, 1 = joueur 1, 2 = joueur 2
        self.board = [[0 for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]

        # Initialisation des positions de départ
        # Joueur 1 (rouge) en haut
        self.board[0][0] = 1
        self.board[0][1] = 1
        self.board[0][2] = 1

        # Joueur 2 (bleu) en bas
        self.board[2][0] = 2
        self.board[2][1] = 2
        self.board[2][2] = 2

        self.player = 1  # Joueur 1 commence
        self.game_over = False
        self.winner = None
        self.selected_piece = None
        self.valid_moves = []
        self.score = {1: 0, 2: 0}  # Score tracking
        self.phase = "moving"  # Game phase tracking

        # AI settings
        self.ai_enabled = False
        self.ai_player = 2  # AI plays as player 2 (blue)
        self.ai_type = 'astar'  # Changed default to astar
        self.ai_difficulty = 'easy'  # Changed default to easy
        self.ai = None
        self.update_ai()

        # Définition des mouvements valides pour chaque position
        self.valid_connections = self.create_valid_connections()

        # Liste des connexions pour le rendu visuel
        self.visual_connections = [
            # Connexions horizontales
            ((0, 0), (0, 1)), ((0, 1), (0, 2)),
            ((1, 0), (1, 1)), ((1, 1), (1, 2)),
            ((2, 0), (2, 1)), ((2, 1), (2, 2)),

            # Connexions verticales
            ((0, 0), (1, 0)), ((1, 0), (2, 0)),
            ((0, 1), (1, 1)), ((1, 1), (2, 1)),
            ((0, 2), (1, 2)), ((1, 2), (2, 2)),

            # Connexions diagonales en X
            ((0, 0), (1, 1)), ((1, 1), (2, 2)),
            ((0, 2), (1, 1)), ((1, 1), (2, 0))
        ]

        # Boutons
        button_width = 300
        self.reset_button = Button(620, 500, button_width, 50, "Recommencer", self.reset)
        self.quit_button = Button(620, 560, button_width, 50, "Quitter", self.quit_game)
        
        # AI control buttons
        self.ai_toggle_button = Button(620, 150, button_width, 50, "AI: OFF", self.toggle_ai)
        self.ai_type_button = Button(620, 210, button_width, 50, "AI: A*", self.toggle_ai_type)
        self.difficulty_button = Button(620, 270, button_width, 50, "Difficulty: Easy", self.toggle_difficulty)

    def create_valid_connections(self):
        # Création d'un dictionnaire avec tous les mouvements valides pour chaque position
        connections = {}

        # Pour chaque case du plateau
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                connections[(row, col)] = []

                # Mouvements horizontaux et verticaux (toujours permis vers des cases adjacentes)
                # Haut
                if row > 0:
                    connections[(row, col)].append((row - 1, col))
                # Bas
                if row < BOARD_ROWS - 1:
                    connections[(row, col)].append((row + 1, col))
                # Gauche
                if col > 0:
                    connections[(row, col)].append((row, col - 1))
                # Droite
                if col < BOARD_COLS - 1:
                    connections[(row, col)].append((row, col + 1))

                # Mouvements diagonaux (seulement les diagonales principales "en X")
                # Coin haut-gauche vers coin bas-droite
                if (row == 0 and col == 0) or (row == 2 and col == 2):
                    if (row == 0 and col == 0):
                        connections[(row, col)].append((1, 1))  # vers le centre
                    if (row == 2 and col == 2):
                        connections[(row, col)].append((1, 1))  # vers le centre

                # Coin haut-droite vers coin bas-gauche
                if (row == 0 and col == 2) or (row == 2 and col == 0):
                    if (row == 0 and col == 2):
                        connections[(row, col)].append((1, 1))  # vers le centre
                    if (row == 2 and col == 0):
                        connections[(row, col)].append((1, 1))  # vers le centre

                # Centre vers les quatre coins
                if row == 1 and col == 1:
                    connections[(row, col)].append((0, 0))  # haut-gauche
                    connections[(row, col)].append((0, 2))  # haut-droite
                    connections[(row, col)].append((2, 0))  # bas-gauche
                    connections[(row, col)].append((2, 2))  # bas-droite

        return connections

    def draw_board(self):
        # Fond
        screen.fill(BG_COLOR)

        # Dessiner le plateau de jeu (zone principale)
        pygame.draw.rect(screen, (220, 220, 210), (50, 50, 450, 450), border_radius=10)

        # Dessiner les points (intersections) où les pions peuvent être placés
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                center_x = 50 + col * CELL_SIZE + CELL_SIZE // 2
                center_y = 50 + row * CELL_SIZE + CELL_SIZE // 2
                pygame.draw.circle(screen, BLACK, (center_x, center_y), 8)

        # Dessiner les lignes de connexion
        for start, end in self.visual_connections:
            start_row, start_col = start
            end_row, end_col = end

            start_x = 50 + start_col * CELL_SIZE + CELL_SIZE // 2
            start_y = 50 + start_row * CELL_SIZE + CELL_SIZE // 2
            end_x = 50 + end_col * CELL_SIZE + CELL_SIZE // 2
            end_y = 50 + end_row * CELL_SIZE + CELL_SIZE // 2

            pygame.draw.line(
                screen,
                LINE_COLOR,
                (start_x, start_y),
                (end_x, end_y),
                LINE_WIDTH // 2
            )

        # Dessiner les pions
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                center_x = 50 + col * CELL_SIZE + CELL_SIZE // 2
                center_y = 50 + row * CELL_SIZE + CELL_SIZE // 2

                if self.board[row][col] == 1:
                    color = RED
                    pygame.draw.circle(screen, color, (center_x, center_y), PION_RADIUS)
                elif self.board[row][col] == 2:
                    color = BLUE
                    pygame.draw.circle(screen, color, (center_x, center_y), PION_RADIUS)

        # Surbrillance de la pièce sélectionnée
        if self.selected_piece:
            row, col = self.selected_piece
            center_x = 50 + col * CELL_SIZE + CELL_SIZE // 2
            center_y = 50 + row * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.circle(screen, HIGHLIGHT_COLOR, (center_x, center_y), PION_RADIUS + 5, 5)

        # Afficher les mouvements valides
        for row, col in self.valid_moves:
            center_x = 50 + col * CELL_SIZE + CELL_SIZE // 2
            center_y = 50 + row * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.circle(screen, HIGHLIGHT_COLOR, (center_x, center_y), 10)

        # Dessiner la barre latérale
        self.draw_sidebar()

    def draw_sidebar(self):
        # Panneau latéral
        pygame.draw.rect(screen, SIDEBAR_COLOR, (600, 0, 400, HEIGHT))

        # Tour du joueur
        if not self.game_over:
            player_text = f"Tour: Joueur {self.player}"
            color_indicator = RED if self.player == 1 else BLUE
        else:
            player_text = "Partie terminée"
            color_indicator = (100, 100, 100)

        text_surf = FONT.render(player_text, True, BLACK)
        screen.blit(text_surf, (620, 50))
        pygame.draw.circle(screen, color_indicator, (700, 90), 20)

        # AI control buttons
        self.ai_toggle_button.draw()
        self.ai_type_button.draw()
        self.difficulty_button.draw()

        # Score
        score_text = "Score:"
        text_surf = FONT.render(score_text, True, BLACK)
        screen.blit(text_surf, (620, 350))

        # Score Joueur 1 (Rouge)
        score1_text = f"Joueur 1 (Rouge): {self.score[1]}"
        text_surf = FONT.render(score1_text, True, RED)
        screen.blit(text_surf, (620, 390))

        # Score Joueur 2 (Bleu)
        score2_text = f"Joueur 2 (Bleu): {self.score[2]}"
        text_surf = FONT.render(score2_text, True, BLUE)
        screen.blit(text_surf, (620, 430))

        # Message de victoire
        if self.game_over:
            if self.winner:
                winner_text = f"Joueur {self.winner} a gagné!"
                winner_color = RED if self.winner == 1 else BLUE
            else:
                winner_text = "Match nul!"
                winner_color = BLACK
            text_surf = FONT.render(winner_text, True, winner_color)
            screen.blit(text_surf, (620, 470))

        # Draw control buttons
        self.reset_button.draw()
        self.quit_button.draw()

    def get_row_col_from_mouse(self, mouse_pos):
        x, y = mouse_pos
        row = y // CELL_SIZE
        col = x // CELL_SIZE
        return row, col

    def get_valid_moves(self, row, col):
        # Retourne les mouvements valides pour une pièce à la position (row, col)
        valid = []

        # Obtenir tous les mouvements possibles pour cette position selon la structure du jeu
        possible_moves = self.valid_connections.get((row, col), [])

        # Filtrer pour ne garder que les cases vides
        for new_row, new_col in possible_moves:
            if self.board[new_row][new_col] == 0:
                valid.append((new_row, new_col))

        return valid

    def check_win(self):
        # Vérifier si tous les pions du joueur 1 sont sur la première ligne (bord initial)
        player1_on_start_row = True
        for col in range(BOARD_COLS):
            if self.board[0][col] != 1:
                player1_on_start_row = False
                break

        # Si tous les pions du joueur 1 sont sur sa ligne de départ, il ne peut pas gagner
        if player1_on_start_row:
            return None

        # Vérifier si tous les pions du joueur 2 sont sur la dernière ligne (bord initial)
        player2_on_start_row = True
        for col in range(BOARD_COLS):
            if self.board[2][col] != 2:
                player2_on_start_row = False
                break

        # Si tous les pions du joueur 2 sont sur sa ligne de départ, il ne peut pas gagner
        if player2_on_start_row:
            return None

        # Vérifier les lignes
        for row in range(BOARD_ROWS):
            if self.board[row][0] != 0 and self.board[row][0] == self.board[row][1] == self.board[row][2]:
                return self.board[row][0]

        # Vérifier les colonnes
        for col in range(BOARD_COLS):
            if self.board[0][col] != 0 and self.board[0][col] == self.board[1][col] == self.board[2][col]:
                return self.board[0][col]

        # Vérifier les diagonales
        if self.board[0][0] != 0 and self.board[0][0] == self.board[1][1] == self.board[2][2]:
            return self.board[0][0]
        if self.board[0][2] != 0 and self.board[0][2] == self.board[1][1] == self.board[2][0]:
            return self.board[0][2]

        return None

    def handle_click(self, mouse_pos):
        # Create a mouse button down event
        mouse_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': mouse_pos})

        # Handle AI control buttons first
        if self.ai_toggle_button.handle_event(mouse_event):
            print("AI toggle button clicked")  # Debug print
            return
        if self.ai_type_button.handle_event(mouse_event):
            return
        if self.difficulty_button.handle_event(mouse_event):
            return

        # Handle other buttons
        if self.reset_button.handle_event(mouse_event):
            return
        if self.quit_button.handle_event(mouse_event):
            return

        # If the game is over, don't allow moves
        if self.game_over:
            return

        # Convert mouse position to board coordinates
        x, y = mouse_pos
        if x < 50 or x > 500 or y < 50 or y > 500:  # Check if click is in board area
            return

        row = (y - 50) // CELL_SIZE
        col = (x - 50) // CELL_SIZE

        # If a piece is already selected, try to move it
        if self.selected_piece:
            if (row, col) in self.valid_moves:
                # Move the piece
                old_row, old_col = self.selected_piece
                self.board[row][col] = self.board[old_row][old_col]
                self.board[old_row][old_col] = 0
                self.selected_piece = None
                self.valid_moves = []

                # Check for win
                winner = self.check_win()
                if winner:
                    self.game_over = True
                    self.winner = winner
                    self.score[winner] += 1
                else:
                    self.player = 3 - self.player  # Switch players
                    
                    # If AI is enabled and it's AI's turn, make AI move
                    if self.ai_enabled and self.player == self.ai_player:
                        self.make_ai_move()
            else:
                # If clicking on another piece of the same player, select it
                if 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS:
                    if self.board[row][col] == self.player:
                        self.selected_piece = (row, col)
                        self.valid_moves = self.get_valid_moves(row, col)
                    else:
                        self.selected_piece = None
                        self.valid_moves = []
        else:
            # Select a piece
            if 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS:
                if self.board[row][col] == self.player:
                    self.selected_piece = (row, col)
                    self.valid_moves = self.get_valid_moves(row, col)

    def reset(self):
        # Save current settings
        current_score = self.score.copy()
        current_ai_enabled = self.ai_enabled
        current_ai_type = self.ai_type
        current_ai_difficulty = self.ai_difficulty
        
        # Reset the game
        self.__init__()
        
        # Restore settings
        self.score = current_score
        self.ai_enabled = current_ai_enabled
        self.ai_type = current_ai_type
        self.ai_difficulty = current_ai_difficulty
        self.ai_toggle_button.text = "AI: ON" if self.ai_enabled else "AI: OFF"
        self.ai_type_button.text = f"AI: {self.ai_type.capitalize()}"
        self.difficulty_button.text = f"Difficulty: {self.ai_difficulty.capitalize()}"
        self.update_ai()

        # If AI is enabled and it's AI's turn, make the first move
        if self.ai_enabled and self.player == self.ai_player:
            self.make_ai_move()

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def update_ai(self):
        """Update the AI instance based on current settings."""
        if self.ai_type == 'minimax':
            self.ai = ThreeMensMorrisAI(self.ai_difficulty)
        else:  # astar
            self.ai = ThreeMensMorrisAStar(self.ai_difficulty)
        print(f"AI updated: {self.ai_type} with difficulty {self.ai_difficulty}")  # Debug print

    def toggle_ai(self):
        """Toggle AI on/off."""
        print("Toggling AI")  # Debug print
        self.ai_enabled = not self.ai_enabled
        self.ai_toggle_button.text = "AI: ON" if self.ai_enabled else "AI: OFF"
        print(f"AI enabled: {self.ai_enabled}")  # Debug print
        if self.ai_enabled:
            self.reset()  # Reset the game when enabling AI
            # If it's AI's turn, make the first move
            if self.player == self.ai_player:
                self.make_ai_move()

    def toggle_ai_type(self):
        """Toggle between Minimax and A* AI."""
        self.ai_type = 'astar' if self.ai_type == 'minimax' else 'minimax'
        self.ai_type_button.text = f"AI: {self.ai_type.capitalize()}"
        self.update_ai()
        # Reset the game to ensure proper AI initialization
        self.reset()

    def toggle_difficulty(self):
        """Cycle through difficulty levels."""
        difficulties = ['easy', 'medium', 'hard']
        current_index = difficulties.index(self.ai_difficulty)
        self.ai_difficulty = difficulties[(current_index + 1) % len(difficulties)]
        self.difficulty_button.text = f"Difficulty: {self.ai_difficulty.capitalize()}"
        self.update_ai()

    def make_ai_move(self):
        """Make an AI move."""
        if not self.ai_enabled or self.game_over or self.player != self.ai_player:
            return

        print(f"\nAI making move with {self.ai_type}")  # Debug print
        print("Current board state:")  # Debug print
        for row in self.board:
            print(row)
        print(f"AI is player {self.ai_player}")  # Debug print
        
        # First verify that the AI has pieces on the board
        ai_pieces = []
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == self.ai_player:
                    ai_pieces.append((row, col))
        
        if not ai_pieces:
            print("No AI pieces found on the board!")  # Debug print
            return
            
        print(f"Found AI pieces at: {ai_pieces}")  # Debug print
        
        # Get AI's move
        move = self.ai.get_best_move(self.board, self.ai_player)
        if move:
            (from_row, from_col), (to_row, to_col) = move
            print(f"AI attempting move from ({from_row}, {from_col}) to ({to_row}, {to_col})")  # Debug print
            
            # Verify the move is valid
            if (0 <= from_row < 3 and 0 <= from_col < 3 and 
                0 <= to_row < 3 and 0 <= to_col < 3 and
                self.board[from_row][from_col] == self.ai_player and  # Must be AI's piece
                self.board[to_row][to_col] == 0):  # Must be empty
                
                # Verify the move follows game rules
                is_valid_move = False
                
                # Check if it's a diagonal move
                if from_row != to_row and from_col != to_col:
                    # Diagonal moves must follow the X pattern
                    if ((from_row == 0 and from_col == 0 and to_row == 1 and to_col == 1) or
                        (from_row == 0 and from_col == 2 and to_row == 1 and to_col == 1) or
                        (from_row == 2 and from_col == 0 and to_row == 1 and to_col == 1) or
                        (from_row == 2 and from_col == 2 and to_row == 1 and to_col == 1) or
                        (from_row == 1 and from_col == 1 and to_row == 0 and to_col == 0) or
                        (from_row == 1 and from_col == 1 and to_row == 0 and to_col == 2) or
                        (from_row == 1 and from_col == 1 and to_row == 2 and to_col == 0) or
                        (from_row == 1 and from_col == 1 and to_row == 2 and to_col == 2)):
                        is_valid_move = True
                else:
                    # Horizontal or vertical moves must be to adjacent squares
                    if abs(from_row - to_row) + abs(from_col - to_col) == 1:
                        is_valid_move = True
                
                if is_valid_move:
                    # Make the move
                    self.board[to_row][to_col] = self.board[from_row][from_col]
                    self.board[from_row][from_col] = 0
                    
                    print("Board after AI move:")  # Debug print
                    for row in self.board:
                        print(row)

                    # Check for win
                    winner = self.check_win()
                    if winner:
                        self.game_over = True
                        self.winner = winner
                        self.score[winner] += 1
                    else:
                        self.player = 3 - self.player  # Switch to human player
                else:
                    print("Move violates game rules")  # Debug print
            else:
                print("Invalid move attempted by AI")  # Debug print
                print(f"From: ({from_row}, {from_col}) = {self.board[from_row][from_col]}")
                print(f"To: ({to_row}, {to_col}) = {self.board[to_row][to_col]}")
                print(f"AI is player {self.ai_player}")  # Debug print
        else:
            print("AI couldn't find a valid move")  # Debug print
            print("Current board state when no move found:")  # Debug print
            for row in self.board:
                print(row)


# Création du jeu
game = Game()

# Boucle principale
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            game.handle_click(pygame.mouse.get_pos())

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # Touche R pour recommencer
                game.reset()

    # Dessiner le plateau
    game.draw_board()

    # Mettre à jour l'affichage
    pygame.display.update()

    # Limiter la fréquence d'images
    pygame.time.Clock().tick(60)