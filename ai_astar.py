import heapq
from typing import List, Tuple, Dict, Set
import copy
from game_logic import create_valid_connections, get_valid_moves, is_winning_state

class ThreeMensMorrisAStar:
    def __init__(self, difficulty: str = 'medium'):
        self.difficulty = difficulty
        # Adjust search depth based on difficulty
        self.max_depth = {
            'easy': 2,
            'medium': 3,
            'hard': 4
        }.get(difficulty, 3)
        # Create valid connections for move validation
        self.valid_connections = create_valid_connections()

    def get_best_move(self, board: List[List[int]], player: int) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        Find the best move using A* algorithm
        Returns: ((from_row, from_col), (to_row, to_col))
        """
        # First check if there are any valid moves
        valid_moves = self.get_valid_moves(board, player)
        if not valid_moves:
            return None  # No valid moves available

        # Priority queue for A* search
        # Format: (f_score, move_count, board_state, move)
        open_set = []
        # Set to keep track of visited states
        closed_set = set()
        # Dictionary to store g_scores (cost from start to current)
        g_score = {}
        # Dictionary to store f_scores (g_score + heuristic)
        f_score = {}
        
        # Initialize with current board state
        board_key = self.get_board_state_key(board)
        g_score[board_key] = 0
        f_score[board_key] = self.heuristic(board, player)
        heapq.heappush(open_set, (f_score[board_key], 0, board, None))
        
        while open_set and len(closed_set) < self.max_depth * 100:  # Limit search depth
            # Get the state with lowest f_score
            current_f, move_count, current_board, current_move = heapq.heappop(open_set)
            current_key = self.get_board_state_key(current_board)
            
            # Skip if we've seen this state
            if current_key in closed_set:
                continue
                
            # Add to closed set
            closed_set.add(current_key)
            
            # If this is a winning state, return the move that led to it
            if is_winning_state(current_board, player):
                return current_move if current_move else valid_moves[0]
            
            # Get all valid moves from current state
            current_valid_moves = self.get_valid_moves(current_board, player)
            if not current_valid_moves:
                continue  # Skip if no valid moves from this state
            
            for from_pos, to_pos in current_valid_moves:
                # Create new board state
                new_board = copy.deepcopy(current_board)
                from_row, from_col = from_pos
                to_row, to_col = to_pos
                new_board[to_row][to_col] = new_board[from_row][from_col]
                new_board[from_row][from_col] = 0
                
                new_key = self.get_board_state_key(new_board)
                
                # Calculate new g_score
                tentative_g_score = g_score[current_key] + 1
                
                # If this is a better path to this state
                if new_key not in g_score or tentative_g_score < g_score[new_key]:
                    g_score[new_key] = tentative_g_score
                    f_score[new_key] = tentative_g_score + self.heuristic(new_board, player)
                    
                    # If this is the first move, store it
                    move_to_store = current_move if current_move else (from_pos, to_pos)
                    
                    # Add to open set
                    heapq.heappush(open_set, (f_score[new_key], move_count + 1, new_board, move_to_store))
        
        # If we haven't found a winning state, return the move that leads to the best heuristic value
        best_move = None
        best_heuristic = float('inf')
        
        for from_pos, to_pos in valid_moves:
            new_board = copy.deepcopy(board)
            from_row, from_col = from_pos
            to_row, to_col = to_pos
            new_board[to_row][to_col] = new_board[from_row][from_col]
            new_board[from_row][from_col] = 0
            
            h = self.heuristic(new_board, player)
            if h < best_heuristic:
                best_heuristic = h
                best_move = (from_pos, to_pos)
        
        return best_move

    def get_valid_moves(self, board: List[List[int]], player: int) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Get all valid moves for the current player using the game's validation logic
        Returns: List of ((from_row, from_col), (to_row, to_col)) tuples
        """
        valid_moves = []
        
        # Find all player's pieces
        for row in range(3):
            for col in range(3):
                if board[row][col] == player:
                    # Use the game logic's get_valid_moves function
                    possible_moves = get_valid_moves(board, row, col, self.valid_connections)
                    for new_row, new_col in possible_moves:
                        valid_moves.append(((row, col), (new_row, new_col)))
        
        return valid_moves

    def heuristic(self, board: List[List[int]], player: int) -> float:
        """
        Calculate heuristic value for the current board state
        Lower values are better for the current player
        """
        score = 0
        opponent = 3 - player

        # Check rows
        for row in range(3):
            player_count = 0
            opponent_count = 0
            for col in range(3):
                if board[row][col] == player:
                    player_count += 1
                elif board[row][col] == opponent:
                    opponent_count += 1
            # Reward for having more pieces in a row
            score -= (player_count * 2)
            # Penalize opponent's pieces in a row
            score += (opponent_count * 2)

        # Check columns
        for col in range(3):
            player_count = 0
            opponent_count = 0
            for row in range(3):
                if board[row][col] == player:
                    player_count += 1
                elif board[row][col] == opponent:
                    opponent_count += 1
            score -= (player_count * 2)
            score += (opponent_count * 2)

        # Check diagonals
        # Main diagonal (top-left to bottom-right)
        player_count = 0
        opponent_count = 0
        for i in range(3):
            if board[i][i] == player:
                player_count += 1
            elif board[i][i] == opponent:
                opponent_count += 1
        score -= (player_count * 2)
        score += (opponent_count * 2)

        # Secondary diagonal (top-right to bottom-left)
        player_count = 0
        opponent_count = 0
        for i in range(3):
            if board[i][2-i] == player:
                player_count += 1
            elif board[i][2-i] == opponent:
                opponent_count += 1
        score -= (player_count * 2)
        score += (opponent_count * 2)

        return score

    def get_board_state_key(self, board: List[List[int]]) -> str:
        """
        Convert board state to a string key for hashing
        """
        return ''.join(str(cell) for row in board for cell in row) 