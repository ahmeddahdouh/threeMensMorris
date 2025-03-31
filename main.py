import pygame
import math

# Initialisation de pygame
pygame.init()

# Définition des constantes
WIDTH, HEIGHT = 1000, 600
BACKGROUND_COLOR = (240, 240, 235)
LINE_COLOR = (50, 50, 50)
LINE_WIDTH = 5
CIRCLE_RADIUS = 35
PLAYER_COLORS = [(220, 50, 50), (50, 50, 220)]  # Rouge et Bleu
FONT = pygame.font.Font(None, 36)
BUTTON_COLOR = (100, 180, 100)
BUTTON_HOVER_COLOR = (120, 200, 120)
BUTTON_TEXT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (120, 255, 120, 150)  # Couleur de surbrillance pour les positions possibles

# Création de la fenêtre
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Three Men's Morris Amélioré")

# Coordonnées des positions du plateau (9 cases)
positions = [
    (200, 100), (350, 100), (500, 100),
    (200, 250), (350, 250), (500, 250),
    (200, 400), (350, 400), (500, 400)
]

# Combinaisons gagnantes
WINNING_COMBINATIONS = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Lignes
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Colonnes
    (0, 4, 8), (2, 4, 6)  # Diagonales
]

# État du jeu
board = [None] * 9  # None = case vide, 0 = joueur 1, 1 = joueur 2
current_player = 0  # Alterne entre 0 (rouge) et 1 (bleu)
phase = "placing"  # "placing" (placer pions) ou "moving" (déplacer pions)
selected_piece = None  # Stocke l'index du pion sélectionné
player_pieces = {0: [], 1: []}  # Stocke les pions placés pour chaque joueur
game_active = True
score = {0: 0, 1: 0}  # Score pour chaque joueur
victory_displayed = False  # Indicateur pour éviter les mises à jour multiples du score
winner = None  # Variable pour stocker le gagnant

# Animation
animations = []  # Liste pour stocker les animations en cours
animation_speed = 10  # Vitesse de l'animation

# Adjacence des positions
adjacent_positions = {
    0: [1, 3, 4], 1: [0, 2, 4], 2: [1, 4, 5],
    3: [0, 4, 6], 4: [0, 1, 2, 3, 5, 6, 7, 8], 5: [2, 4, 8],
    6: [3, 4, 7], 7: [4, 6, 8], 8: [4, 5, 7]
}


# Classe pour boutons
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


# Classe d'animation pour les pions
class PieceAnimation:
    def __init__(self, start_pos, end_pos, color, duration=30):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = color
        self.duration = duration
        self.progress = 0
        self.active = True

    def update(self):
        if self.progress < self.duration:
            self.progress += 1
        else:
            self.active = False

    def draw(self):
        if not self.active:
            return

        progress_ratio = self.progress / self.duration
        current_x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * progress_ratio
        current_y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * progress_ratio

        # Effet de rebond
        bounce = math.sin(progress_ratio * math.pi) * 5

        pygame.draw.circle(screen, self.color, (int(current_x), int(current_y - bounce)), CIRCLE_RADIUS)

        # Ajouter un petit éclat
        if progress_ratio > 0.8:
            shine_alpha = int(255 * (1 - (progress_ratio - 0.8) / 0.2))
            shine_surf = pygame.Surface((CIRCLE_RADIUS * 2, CIRCLE_RADIUS * 2), pygame.SRCALPHA)
            pygame.draw.circle(shine_surf, (255, 255, 255, shine_alpha), (CIRCLE_RADIUS, CIRCLE_RADIUS),
                               CIRCLE_RADIUS // 2)
            screen.blit(shine_surf, (int(current_x - CIRCLE_RADIUS), int(current_y - bounce - CIRCLE_RADIUS)))


# Fonction pour créer une animation de mouvement
def create_move_animation(start_index, end_index, player):
    start_pos = positions[start_index]
    end_pos = positions[end_index]
    color = PLAYER_COLORS[player]
    animations.append(PieceAnimation(start_pos, end_pos, color))


# Fonction pour créer une animation d'apparition
def create_place_animation(index, player):
    pos = positions[index]
    # Animation d'apparition depuis hors-écran
    if player == 0:  # Joueur rouge vient de la gauche
        start_pos = (-50, pos[1])
    else:  # Joueur bleu vient de la droite
        start_pos = (WIDTH + 50, pos[1])

    color = PLAYER_COLORS[player]
    animations.append(PieceAnimation(start_pos, pos, color))


# Fonction pour obtenir les positions possibles pour un pion sélectionné
def get_possible_moves(piece_index):
    if phase == "placing":
        return [i for i, cell in enumerate(board) if cell is None]
    elif phase == "moving":
        return [i for i in adjacent_positions[piece_index] if board[i] is None]
    return []


# Fonction pour dessiner le plateau
def draw_board():
    screen.fill(BACKGROUND_COLOR)

    # Dessiner la zone de jeu
    pygame.draw.rect(screen, (220, 220, 210), (150, 50, 400, 400), border_radius=10)

    # Lignes du plateau
    pygame.draw.line(screen, LINE_COLOR, positions[0], positions[2], LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, positions[3], positions[5], LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, positions[6], positions[8], LINE_WIDTH)

    pygame.draw.line(screen, LINE_COLOR, positions[0], positions[6], LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, positions[1], positions[7], LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, positions[2], positions[8], LINE_WIDTH)

    pygame.draw.line(screen, LINE_COLOR, positions[0], positions[8], LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, positions[2], positions[6], LINE_WIDTH)

    # Dessiner les points aux intersections
    for pos in positions:
        pygame.draw.circle(screen, LINE_COLOR, pos, 10)

    # Dessiner les surbrillances des positions possibles
    if selected_piece is not None and phase == "moving":
        possible_moves = get_possible_moves(selected_piece)
        for move_index in possible_moves:
            # Créer une surface semi-transparente pour la surbrillance
            highlight_surf = pygame.Surface((CIRCLE_RADIUS * 2, CIRCLE_RADIUS * 2), pygame.SRCALPHA)
            pygame.draw.circle(highlight_surf, HIGHLIGHT_COLOR, (CIRCLE_RADIUS, CIRCLE_RADIUS), CIRCLE_RADIUS)
            screen.blit(highlight_surf,
                        (positions[move_index][0] - CIRCLE_RADIUS, positions[move_index][1] - CIRCLE_RADIUS))

            # Dessiner un cercle pulsant
            pulse = math.sin(pygame.time.get_ticks() / 200) * 5
            pygame.draw.circle(screen, (100, 255, 100), positions[move_index], int(CIRCLE_RADIUS + pulse), 2)

    # Dessiner les pions placés
    for i, player in enumerate(board):
        if player is not None:
            color = PLAYER_COLORS[player]

            # Vérifier si le pion est sélectionné
            if i == selected_piece:
                # Dessiner un contour pour indiquer la sélection
                pygame.draw.circle(screen, (255, 255, 0), positions[i], CIRCLE_RADIUS + 5)

            pygame.draw.circle(screen, color, positions[i], CIRCLE_RADIUS)

            # Ajouter un peu de style aux pions
            highlight = (min(color[0] + 50, 255), min(color[1] + 50, 255), min(color[2] + 50, 255))
            pygame.draw.circle(screen, highlight, (positions[i][0] - 10, positions[i][1] - 10), 10)

    # Afficher les animations en cours
    for anim in animations[:]:
        anim.update()
        anim.draw()
        if not anim.active:
            animations.remove(anim)

    # Interface utilisateur
    draw_ui()

    # Vérifier et afficher un message si un joueur gagne
    global winner, victory_displayed
    current_winner = check_winner()

    if current_winner is not None and not victory_displayed:
        winner = current_winner
        show_winner(winner)
        victory_displayed = True


# Fonction pour dessiner l'interface utilisateur
def draw_ui():
    # Panneau latéral
    pygame.draw.rect(screen, (200, 200, 190), (600, 0, 400, HEIGHT))

    # Tour du joueur
    if game_active:
        player_text = f"Tour: Joueur {current_player + 1}"
        color_indicator = PLAYER_COLORS[current_player]
    else:
        player_text = "Partie terminée"
        color_indicator = (100, 100, 100)

    text_surf = FONT.render(player_text, True, (0, 0, 0))
    screen.blit(text_surf, (620, 50))
    pygame.draw.circle(screen, color_indicator, (700, 90), 20)

    # Phase de jeu
    phase_text = "Phase: Placement" if phase == "placing" else "Phase: Déplacement"
    text_surf = FONT.render(phase_text, True, (0, 0, 0))
    screen.blit(text_surf, (620, 120))

    # Scores
    score_text = f"Score - Rouge: {score[0]}  Bleu: {score[1]}"
    text_surf = FONT.render(score_text, True, (0, 0, 0))
    screen.blit(text_surf, (620, 160))

    # Aide
    if game_active:
        if phase == "placing":
            help_text = f"Placez vos 3 pions"
            text_surf = FONT.render(help_text, True, (80, 80, 80))
            screen.blit(text_surf, (620, 200))
        elif phase == "moving":
            if selected_piece is None:
                help_text = "Sélectionnez un pion"
            else:
                help_text = "Choisissez où déplacer"
            text_surf = FONT.render(help_text, True, (80, 80, 80))
            screen.blit(text_surf, (620, 200))
    else:
        help_text = "Cliquez sur Nouvelle Partie pour continuer"
        text_surf = FONT.render(help_text, True, (80, 80, 80))
        screen.blit(text_surf, (620, 200))

    # Dessiner les boutons
    for button in buttons:
        button.draw()

    # Instructions du jeu
    draw_instructions()


# Fonction pour afficher les instructions du jeu
def draw_instructions():
    pygame.draw.rect(screen, (240, 240, 220), (620, 400, 350, 180), border_radius=8)
    pygame.draw.rect(screen, (100, 100, 100), (620, 400, 350, 180), 2, border_radius=8)

    title = FONT.render("Comment jouer", True, (50, 50, 50))
    screen.blit(title, (670, 410))

    instructions = [
        "1. Placez 3 pions à tour de rôle",
        "2. Puis déplacez vos pions vers une",
        "   case adjacente libre",
        "3. Alignez 3 pions pour gagner!"
    ]

    small_font = pygame.font.Font(None, 24)
    for i, text in enumerate(instructions):
        instruction = small_font.render(text, True, (50, 50, 50))
        screen.blit(instruction, (630, 450 + i * 30))


# Afficher le gagnant
def show_winner(winner):
    global game_active
    game_active = False

    # Mettre à jour le score
    score[winner] += 1

    # Dessiner un panneau de victoire
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))

    message = f"Joueur {winner + 1} gagne !"
    color = PLAYER_COLORS[winner]

    text = FONT.render(message, True, (255, 255, 255))

    # Créer un panneau de victoire plus grand
    panel_width, panel_height = 400, 200
    panel_x = WIDTH // 2 - panel_width // 2
    panel_y = HEIGHT // 2 - panel_height // 2

    pygame.draw.rect(screen, (50, 50, 50), (panel_x, panel_y, panel_width, panel_height), border_radius=15)
    pygame.draw.rect(screen, color, (panel_x, panel_y, panel_width, panel_height), 4, border_radius=15)

    # Ajouter le message principal
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, panel_y + 50))

    # Ajouter un message supplémentaire
    subtext = FONT.render("Cliquez sur Nouvelle Partie", True, (200, 200, 200))
    screen.blit(subtext, (WIDTH // 2 - subtext.get_width() // 2, panel_y + 100))

    # Mettre en surbrillance la combinaison gagnante
    highlight_winning_combination()


# Fonction pour mettre en surbrillance la combinaison gagnante
def highlight_winning_combination():
    for combo in WINNING_COMBINATIONS:
        a, b, c = combo
        if board[a] is not None and board[a] == board[b] == board[c]:
            # Dessiner des lignes lumineuses entre les pions gagnants
            color = PLAYER_COLORS[board[a]]
            bright_color = (min(color[0] + 70, 255), min(color[1] + 70, 255), min(color[2] + 70, 255))

            for i in range(10):  # Animation clignotante
                alpha = int(255 * (0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 200)))
                glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

                # Dessiner une ligne épaisse qui brille
                pygame.draw.line(glow_surf, (*bright_color, alpha),
                                 positions[a], positions[b], LINE_WIDTH + 6)
                pygame.draw.line(glow_surf, (*bright_color, alpha),
                                 positions[b], positions[c], LINE_WIDTH + 6)

                # Ajouter des cercles brillants autour des pions gagnants
                for pos_idx in [a, b, c]:
                    pygame.draw.circle(glow_surf, (*bright_color, alpha),
                                       positions[pos_idx], CIRCLE_RADIUS + 10, 4)

                screen.blit(glow_surf, (0, 0))

            break


# Vérifie si un joueur a gagné
def check_winner():
    for a, b, c in WINNING_COMBINATIONS:
        if board[a] is not None and board[a] == board[b] == board[c]:
            return board[a]
    return None


# Gère le clic du joueur
def handle_click(pos):
    global current_player, phase, selected_piece, game_active, victory_displayed

    # Vérifier si le jeu est actif
    if not game_active:
        return False  # Indiquer qu'aucun mouvement n'a été fait

    # Vérifier si des animations sont en cours
    if animations:
        return False  # Ignorer les clics pendant les animations

    for i, (x, y) in enumerate(positions):
        if abs(pos[0] - x) < CIRCLE_RADIUS and abs(pos[1] - y) < CIRCLE_RADIUS:
            if phase == "placing":
                if board[i] is None and len(player_pieces[current_player]) < 3:
                    board[i] = current_player
                    player_pieces[current_player].append(i)
                    create_place_animation(i, current_player)

                    # Vérifier s'il y a un gagnant après le placement
                    if check_winner() is not None:
                        return True  # Un mouvement a été fait et il y a un gagnant

                    if len(player_pieces[0]) == 3 and len(player_pieces[1]) == 3:
                        phase = "moving"

                    current_player = 1 - current_player
                    return True  # Un mouvement a été fait
                break

            elif phase == "moving":
                if selected_piece is None:
                    if board[i] == current_player:
                        selected_piece = i
                        return True  # Une sélection a été faite
                else:
                    if board[i] is None and is_adjacent(selected_piece, i):
                        create_move_animation(selected_piece, i, current_player)
                        board[i] = current_player
                        board[selected_piece] = None
                        player_pieces[current_player].remove(selected_piece)
                        player_pieces[current_player].append(i)
                        selected_piece = None

                        # Vérifier s'il y a un gagnant après le déplacement
                        if check_winner() is not None:
                            return True  # Un mouvement a été fait et il y a un gagnant

                        current_player = 1 - current_player
                        return True  # Un mouvement a été fait
                    elif board[i] == current_player:
                        selected_piece = i  # Sélectionner un autre pion
                        return True  # Une sélection a été faite
                break

    return False  # Aucun mouvement n'a été fait


# Vérifie si deux positions sont adjacentes
def is_adjacent(start, end):
    return end in adjacent_positions[start]


# Réinitialise le jeu après une victoire
def reset_game():
    global board, current_player, phase, selected_piece, player_pieces, game_active, victory_displayed, winner
    board = [None] * 9
    current_player = 0
    phase = "placing"
    selected_piece = None
    player_pieces = {0: [], 1: []}
    game_active = True
    victory_displayed = False
    winner = None

    # Effacer toutes les animations
    animations.clear()


# Fonction pour quitter le jeu
def quit_game():
    global running
    running = False


# Fonction pour régler la vitesse d'animation
def set_animation_speed(speed):
    global animation_speed
    animation_speed = speed


# Définition des boutons
buttons = [
    Button(620, 250, 200, 50, "Nouvelle Partie", reset_game),
    Button(620, 320, 160, 50, "Quitter", quit_game),
    Button(830, 320, 160, 50, "Aide", lambda: print("Aide")),  # Bouton Aide (à implémenter)
]

# Boucle principale
running = True
clock = pygame.time.Clock()

while running:
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Vérifier si un bouton a été cliqué
            button_clicked = False
            for button in buttons:
                if button.handle_event(event):
                    button_clicked = True
                    break

            # Si aucun bouton n'a été cliqué, traiter comme un clic sur le plateau
            if not button_clicked:
                move_made = handle_click(event.pos)

        # Mise à jour de l'état des boutons (hover)
        for button in buttons:
            button.handle_event(event)

    # Dessiner le plateau et les pions
    draw_board()

    # Mise à jour de l'affichage
    pygame.display.flip()

    # Limiter le taux de rafraîchissement
    clock.tick(60)

pygame.quit()