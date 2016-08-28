class Game(object):
    '''

        menu 1 settings 2 play
            1 asks number of players,board dimension goto meny
        play asks player's name and start
        p1's move
            set move check winner next turn quit (larger number winner)
        future features:
            undo functionality
            computer's move (minmax branch bound and backtracking(game theory)) (first single player and then multi player)
            socket programming
            voice winner
            GUI Tkinter Support (standalone application)
    '''

    nop = 2
    playerlist = []
    board = None

    def __init__(self, nop = 2, width = None, height = None):
        self.nop = nop
        self.board = Board(width, height)

    def display(self):
        print self.board.getboard()


    def start(self):


class Player(object):

    def __init__(self, name, color):
        self.playername = name
        self.color = color

    def get_name(self):

class Board(object):
    '''
        check for recursion depth reached

    '''
    width = 9
    height = 6
    board = None

    def __init__(self, width, height):
        self.board = [[0]*(width+1) for _ in xrange(height+1)]
        self.width = width or self.width
        self.height = height or self.height

    def set(self, x, y, player):
        ch = player.get_name()

    def floodfill(self):


    def is_corner(self, x, y):
        corners = [(1,1), (1,self.width), (self.height,1), (self.height,self.width)]
        return (x,y) in corners

    def is_side(self, x, y):
        return (not self.is_corner(x, y)) and (x == 1 or y == 1 or x == self.height or y == self.width)

    def is_middle(self, x, y):
        return (not self.is_corner(x,y)) and (not self.is_side(x,y))

    def getboard(self):
        #Todo separate presentation and remove hardcoded characters
        s = x = hr = ''
        for i,row in enumerate(self.board):
            x = "|"
            for j,val in enumerate(row):
                x = x + " " + str(val).upper() + " " + "|"
            hr = "=" * len(x)
            s = s + hr + "\n"
            s = s + x + "\n"
        hr = "=" * len(x)
        s = s + hr + "\n"
        return s

def main():
    Game().display()



