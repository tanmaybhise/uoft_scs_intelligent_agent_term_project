import logging

class Hexapawn:
    def __init__(self, size=4):
        self.size = size
        self.board = [[' ' for _ in range(size)] for _ in range(size)]
        self.initialize_board()

    @staticmethod
    def get_actions():
        return {"forward":0,
                "diagonal1":1,
                "diagonal2":2
                }

    def initialize_board(self):
        self.whose_turn = "W"
        self.reward = 0
        self.terminated = False
        for i in range(self.size):
            self.board[0][i] = 'W'  # White pawns
            self.board[self.size - 1][i] = 'B'  # Black pawns
        self.update_state()

    def update_state(self):
        self.state = {"board": self.board, "reward": self.reward, "terminated": self.terminated}

    def print_board(self):
        for row in self.board:
            print(' '.join(row))
        print()

    def is_valid_move(self, start, end, player):
        
        start_x, start_y = start
        end_x, end_y = end

        move_x = end_x - start_x
        move_y = end_y - start_y

        # Check if the move is forward and within one step
        if player == 'W' and move_x != 1:
            logging.error("Invalid forward move")
            return False
        if player == 'B' and move_x != -1:
            logging.error("Invalid forward move")
            return False

        try:
            # Check if the move is straight or diagonal for capture
            if move_y == 0 and self.board[end_x][end_y] == ' ':
                return True
            elif abs(move_y) == 1 and self.board[end_x][end_y] != ' ' and self.board[end_x][end_y] != player:
                return True
        except IndexError:
            return False

        logging.error("Invalid move")
        return False

    def make_move(self, start, end):
        start_x, start_y = start
        end_x, end_y = end
        player = self.board[start_x][start_y]
        self.reward=0
        if player == self.whose_turn:
            pass
        else:
            logging.error(f"Not {player}'s turn")
            self.reward+=-1
            self.update_state()
            return self.state
        if self.is_valid_move(start, end, player):
            self.reward+=1
            self.board[end_x][end_y] = self.board[start_x][start_y]
            self.board[start_x][start_y] = ' '
            self.check_winner()
            if self.whose_turn=="W":
                self.whose_turn="B"
            else:
                self.whose_turn="W"
            self.update_state()
            return self.state
        else:
            self.reward+=-1
        
        self.update_state()
        return self.state
    
    def can_player_move(self, player):
        for x in range(self.size):
            for y in range(self.size):
                if self.board[x][y] == player:
                    # Check all potential moves for the pawn
                    if player == 'W':
                        potential_moves = [(x + 1, y), (x + 1, y - 1), (x + 1, y + 1)]
                    else:
                        potential_moves = [(x - 1, y), (x - 1, y - 1), (x - 1, y + 1)]

                    for move in potential_moves:
                        if 0 <= move[0] < self.size and 0 <= move[1] < self.size:
                            if self.is_valid_move((x, y), move, player):
                                return True
        return False

    def check_winner(self):
        # Check if any pawn has reached the opposite end
        if 'W' in self.board[self.size - 1]:
            self.reward+=1000
            self.terminated = True
            logging.info("W Won!!!")
            return 'W'
        if 'B' in self.board[0]:
            self.reward+=1000
            self.terminated = True
            logging.info("B Won!!!")
            return 'B'

        # Check if players can move
        if not self.can_player_move('W'):
            if self.whose_turn=="B":
                self.reward+=1000
            else:
                self.reward+=-1000
            self.terminated = True
            logging.info("B Won!!!")
            return 'B'
        
        if not self.can_player_move('B'):
            if self.whose_turn=="W":
                self.reward+=1000
            else:
                self.reward+=-1000
            self.terminated = True
            logging.info("W Won!!!")
            return 'W'

        return None

if __name__ == "__main__":
    # Initialize the game and print the starting board
    game = Hexapawn()
    print(game.make_move((0,0), (1,0)))
    print(game.make_move((3,1), (2,1)))
    print(game.make_move((1,0), (2,1)))
    print(game.make_move((3,0), (2,0)))
    #print(game.make_move((2,1), (3,2)))
    print(game.make_move((2,1), (2,0)))
    game.print_board()
