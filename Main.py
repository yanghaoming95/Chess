import AttackPlace
from pathlib import Path
import os
import copy
import sys
import gc
sys.setrecursionlimit(100000)

class Board(object):
    """
    Things Board should do:
    1. Display the whole board.
    2. gernerate a score evaluation to both player1 and player2.
    """

    ''' 10 rows and 9 column chessboard'''
    board = [[None, None, None, None, None, None, None, None, None],
             [None, None, None, None, None, None, None, None, None],
             [None, None, None, None, None, None, None, None, None],
             [None, None, None, None, None, None, None, None, None],
             [None, None, None, None, None, None, None, None, None],
             [None, None, None, None, None, None, None, None, None],
             [None, None, None, None, None, None, None, None, None],
             [None, None, None, None, None, None, None, None, None],
             [None, None, None, None, None, None, None, None, None],
             [None, None, None, None, None, None, None, None, None]]

    def __init__(self, player1, player2):
        self.setup(player1, player2)

    def display(self):
        """
        Print the whole board.
        """
        print("一二三四五六七八九\n------------------")
        for row in self.board:
            result = ""
            for column in row:
                if None == column:
                    result += "  "
                else:
                    result += column.name
            print(result)
        print("------------------\n九八七六五四三二一\n\n")

    def setup(self, player1, player2):
        """
        Initialize the board.
        """
        #initialize the board
        self.player1 = player1
        self.player2 = player2
        self.redg = Chess().Gerneral(player1)
        self.blackg = Chess().Gerneral(player2)
        self.redchecking = False
        self.blackchecking = False
        self.board = self.board_setup(player1,player2)
        self.moveList = {}
        #update positions and places can move
        for row in range(0, 10):
            for column in range(0, 9):
                if None != self.board[row][column]:
                    self.board[row][column].position = [row, column]
                    self.board[row][column].places = Rules(self.board[row][column], self).moveList(check = False)

    def board_setup(self,player1,player2):
        return [[Chess().Rook(player2), Chess().Knight(player2), Chess().Bishop(player2), Chess().Guard(player2), self.blackg, Chess().Guard(player2), Chess().Bishop(player2), Chess().Knight(player2), Chess().Rook(player2)],
                      [None, None, None, None, None, None, None, None, None],
                      [None, Chess().Cannon(player2), None, None, None, None, None, Chess().Cannon(player2), None],
                      [Chess().Pawn(player2), None, Chess().Pawn(player2), None, Chess().Pawn(player2), None, Chess().Pawn(player2), None, Chess().Pawn(player2)],
                      [None, None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None, None],
                      [Chess().Pawn(player1), None, Chess().Pawn(player1), None, Chess().Pawn(player1), None, Chess().Pawn(player1), None, Chess().Pawn(player1)],
                      [None, Chess().Cannon(player1), None, None, None, None, None, Chess().Cannon(player1), None],
                      [None, None, None, None, None, None, None, None, None],
                      [Chess().Rook(player1), Chess().Knight(player1), Chess().Bishop(player1), Chess().Guard(player1), self.redg, Chess().Guard(player1), Chess().Bishop(player1), Chess().Knight(player1), Chess().Rook(player1)]]

    def update(self, player, old_position, new_position):
        """
        Update the board and the position of the chess.
        """

        mychess = self.board[old_position[0]][old_position[1]]
        #if valid chess?
        if mychess is not None and mychess.player == player:
            #update all the potential positions for this chess
            #print(self.board[1][0])
            copy = self.board_copy()
            Rules(mychess, self).applyRules()
            self.board = copy.board
            self.board[old_position[0]][old_position[1]] = mychess
            self.board[new_position[0]][new_position[1]] = mychess
            self.board[old_position[0]][old_position[1]] = None
            self.moveList[old_position] = new_position
            #print(self.board[0][0])
            #print(self.board)
            #change position if it is valid
            if mychess.changePosition(new_position):
                if self.redg.position[1] == self.blackg.position[1]:
                    flag = True
                    for i in range(self.blackg.position[0] + 1, self.redg.position[0]):
                        if old_position[1] == new_position[1]:
                            flag = False
                            break

                        if self.board[i][self.redg.position[1]] is not None and i != old_position[0]:
                            flag = False
                            break
                    if flag:
                        print("Gerneral Meets!")
                        return


            #here need to check if this move is a check or checkmate to another player
        else:
            print(player.name + ", There is no valid chess! Choose another chess.")

    def occupation(self, position):
        if self.board[position[0]][position[1]] == None:
            return False
        return True

    def player_check(self, position):
        '''
        Assume chess is valid, validation outside
        '''
        if self.board[position[0]][position[1]].player.attribute == 1:
            return 1
        return 2
    def check(self, position):
        chess = self.board[position[0]][position[1]]

    def checkmate(self, position):
        ''' Return True if it's a checkmate, otherwise return False'''
        Rules()

    def all_movements(self,players):
        '''
        take in a player and return all it's possible movements
        '''
        ret = {}
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                if self.board[i][j] != None and self.player_check([i,j]) == players.attribute:
                    if self.board[i][j].name not in ret.keys():
                        ret[self.board[i][j].name] = []
                    for item in self.board[i][j].places:
                        if item not in ret[self.board[i][j].name]:
                            ret[self.board[i][j].name].append(item)
        return ret

    def board_copy(self):
        return self.recover_from_movements(self.moveList,self.player1,self.player2)

    def recover_from_movements(self, moveList, player1, player2):
        '''
        Gives the ordered previous movement and recover the board.
        Convetion of moveList: {old_position:new_position}
        '''
        board = Board(player1,player2)
        keys = list(moveList.keys())
        values = list(moveList.values())
        for i in range(len(keys)):
            mychess = board.board[keys[i][0]][keys[i][1]]
            board.board[keys[i][0]][keys[i][1]] = None
            board.board[values[i][0]][values[i][1]] = mychess
            #print(keys[i], values[i])
            board.moveList[keys[i]] = values[i]
        return board

    def one_step_undo(self):
        '''
        for simplicity now, just redo all movements before
        '''

        self.moveList.pop(list(self.moveList.keys())[len(self.moveList.keys()) - 1])
        return self.recover_from_movements(self.moveList,self.player1,self.player2)

class Chess(object):
    '''Red is Player 1 and Black is Player 2'''
    """
    Things Chess should do:
    1. represents all pieces of chess
    """
    def __init__(self):
        """
        1. gives a name for all pieces.
        2. records all places each piece can go.
        3. gives an value of each piece.
        4. record this piece belongs to Player 1 or Player 2.
        5
        """
        self.name = '空'
        self.places = []
        self.player = ''
        self.value = 0
        self.position = [0,0]

    def __str__(self):
        return self.name

    def Rook(self, player):
        if player.attribute == 1:
            self.name = '车'
        else:
            self.name = '車'
        if self.player is '':
            self.player = player
        self.value = 40

        return self

    def Knight(self, player):
        if player.attribute == 1:
            self.name = '马'
        else:
            self.name = '馬'
        if self.player is '':
            self.player = player
        self.value = 15

        return self

    def Bishop(self, player):
        if player.attribute == 1:
            self.name = '相'
        else:
            self.name = '象'
        if self.player is '':
            self.player = player
        self.value = 10

        return self

    def Guard(self, player):
        if player.attribute == 1:
            self.name = '仕'
        else:
            self.name = '士'
        if self.player is '':
            self.player = player
        self.value = 10
        return self

    def Gerneral(self, player):
        if player.attribute == 1:
            self.name = '帅'
        else:
            self.name = '将'
        if self.player is '':
            self.player = player
        self.value = 1000

        return self

    def Pawn(self, player):
        if player.attribute == 1:
            self.name = '兵'
        else:
            self.name = '卒'
        if self.player is '':
            self.player = player
        self.value = 5

        return self

    def Cannon(self, player):
        if player.attribute == 1:
            self.name = '炮'
        else:
            self.name = '砲'
        if self.player is '':
            self.player = player
        self.value = 20
        return self

    def changePosition(self, position):
        """
        Update the position of the chess and return True if the change is valid.
        """
        position = list(position)
        if position in self.places:
            self.position = position
            return True
        else:
            print("Wrong Position! Choose an other position please.")
            return False

    def retrieve_place(self,chess,board):
        return self.chess.places

class Player(object):
    '''
    Things Player class should do:
    1. Record the name of Player if it's not an AI.
    2. If both player are AI, should able to make choices of showing board or not.
    3. Should be the control panel of AI trainning if the choice is AI vs AI.
    '''
    name = ''
    def __init__(self, name, player):
        self.name = name
        self.attribute = player


class Rules(object):
    '''
    Things Rules should do:
    1. Each time When human chooses one piece of chess, gives all potential places this piece can move.
    2. After one move, check if its a checkmate. If it's a checkmate, return end signal; if not, do nothing.

    '''
    def __init__(self, chess, board):
        self.chess = chess
        self.board = board
        self.places = [] #move choices

    def moveList(self, check = True):
        row = self.chess.position[0]
        column = self.chess.position[1]
        resultList = []
        if self.chess.name == '仕':
            #store the potential positions in a list according to the current position
            potentialList = [[row - 1, column - 1], [row - 1, column + 1], [row + 1, column - 1], [row + 1, column + 1]]
            #check if these four positions are in the valid area
            resultList = self.checkBoundary(7, 9, 3, 5, potentialList)
            resultList = [list(x) for x in set(tuple(x) for x in resultList) if
                          self.board.board[x[0]][x[1]] is None or self.board.player_check(x) != 1]

        elif self.chess.name == '士':
            potentialList = [[row - 1, column - 1], [row - 1, column + 1], [row + 1, column - 1], [row + 1, column + 1]]
            resultList = self.checkBoundary(0, 2, 3, 5, potentialList)
            resultList = [list(x) for x in set(tuple(x) for x in resultList) if
                          self.board.board[x[0]][x[1]] is None or self.board.player_check(x) != 2]

        elif self.chess.name == '相':
            #store the potential positions in a list according to the current position
            potentialList = [[row - 2, column - 2], [row - 2, column + 2], [row + 2, column - 2], [row + 2, column + 2]]
            #check if these four positions are in the valid area
            resultList = self.checkBoundary(5, 9, 0, 8, potentialList)
            #check if it gets stuck
            for i in resultList:
                if (self.board.board[(int)((row + i[0])/2)][(int)((column + i[1])/2)] is not None):
                    resultList.remove(i)
            resultList = [list(x) for x in set(tuple(x) for x in resultList) if
                          self.board.board[x[0]][x[1]] is None or self.board.player_check(x) != 1]

        elif self.chess.name == '象':
            potentialList = [[row - 2, column - 2], [row - 2, column + 2], [row + 2, column - 2], [row + 2, column + 2]]
            resultList = self.checkBoundary(0, 4, 0, 8, potentialList)
            for i in resultList:
                if (self.board.board[(row + i[0])//2][(column + i[1])//2] is not None):
                    resultList.remove(i)
                    resultList = [list(x) for x in set(tuple(x) for x in resultList) if
                                  self.board.board[x[0]][x[1]] is None or self.board.player_check(x) != 2]

        elif self.chess.name == '帅':
            potentialList = [[row - 1, column ], [row, column + 1], [row + 1, column ], [row, column - 1]]
            resultList = self.checkBoundary(7, 9, 3, 5, potentialList)
            resultList = [list(x) for x in set(tuple(x) for x in resultList) if
                          self.board.board[x[0]][x[1]] is None or self.board.player_check(x) != 1]

        elif self.chess.name == '将':
            potentialList = [[row - 1, column], [row, column + 1], [row + 1, column], [row, column - 1]]
            resultList = self.checkBoundary(0, 2, 3, 5, potentialList)
            resultList = [list(x) for x in set(tuple(x) for x in resultList) if
                          self.board.board[x[0]][x[1]] is None or self.board.player_check(x) != 2]

        #update all the positions it can go
        elif self.chess.name == '兵':
                if self.chess.position[0] >= 5:
                    potentialList = [[row - 1, column]]
                else:
                    potentialList = [[row - 1, column], [row, column + 1], [row, column - 1]]
                resultList = self.checkBoundary(0, 6, 0, 8,potentialList)
                resultList = [list(x) for x in set(tuple(x) for x in resultList) if
                              self.board.board[x[0]][x[1]] is None or self.board.player_check(x) != 1]

        elif self.chess.name == '卒':
            if self.chess.position[0] <= 4:
                potentialList = [[row + 1, column]]
            else:
                potentialList = [[row + 1, column], [row, column + 1], [row, column - 1]]
            resultList = self.checkBoundary(3, 9, 0, 8, potentialList)
            resultList = [list(x) for x in set(tuple(x) for x in resultList) if
                          self.board.board[x[0]][x[1]] is None or self.board.player_check(x) != 2]

        elif self.chess.name == '马':
            potentialList = [[row + 2, column + 1], [row + 2, column - 1], [row + 1, column + 2],
                             [row + 1, column - 2],
                             [row - 1, column + 2], [row - 1, column - 2], [row - 2, column + 1],
                             [row - 2, column - 1]]
            resultList = self.checkBoundary(0, 9, 0, 8, potentialList)

            # stuck the Knights
            for i in resultList:
                p = abs(i[0] - row) # row diff
                j = abs(i[1] - column) # column diff
                if p == 2: # 南北方向阻挡
                    if self.board.board[int((i[0]+row)/2)][column] is not None:
                        resultList.remove(i)
                else: # 东西方向阻挡
                    if self.board.board[row][int((i[1]+column)/2)] is not None:
                        resultList.remove(i)

            resultList = [list(x) for x in set(tuple(x) for x in resultList) if
                          self.board.board[x[0]][x[1]] is None or self.board.player_check(x) != 1]


        elif self.chess.name == '馬':
            potentialList = [[row + 2, column + 1], [row + 2, column - 1], [row + 1, column + 2 ], [row + 1, column - 2],
                             [row - 1, column + 2], [row - 1, column - 2], [row - 2, column + 1 ], [row - 2, column - 1]]
            resultList = self.checkBoundary(0, 9, 0, 8, potentialList)
            # stuck the Knights
            for i in resultList:
                p = abs(i[0] - row) # row diff
                j = abs(i[1] - column) # column diff
                if p == 2: # 南北方向阻挡
                    if self.board.board[int((i[0]+row)/2)][column] is not None:
                        resultList.remove(i)
                else: # 东西方向阻挡
                    if self.board.board[row][int((i[1]+column)/2)] is not None:
                        resultList.remove(i)

            resultList = [list(x) for x in set(tuple(x) for x in resultList) if
                          self.board.board[x[0]][x[1]] is None or self.board.player_check(x) != 2]

        elif self.chess.name == '车':
            potentialList = []
            row_upper, row_lower, column_upper, column_lower = row, row, column, column
            for i in range(1, 9):
                if row + i > 9:
                    break
                if self.board.board[row + i][column] is not None:
                    if self.board.player_check([row + i, column]) == 2:
                        row_upper = row + i
                        break
                    row_upper = row + i - 1
                    break
            for i in range(1, 9):
                if row - i < 0:
                    break
                if self.board.board[row - i][column] is not None:
                    if self.board.player_check([row - i, column]) == 2:
                        row_lower = row - i
                        break
                    row_lower = row - i + 1
                    break

            for i in range(1, 8):
                if column + i > 8:
                    break
                if self.board.board[row][column + i] is not None:
                    if self.board.player_check([row, column + i]) == 2:
                        column_upper = column + i
                        break
                    column_upper = column + i - 1
                    break

            for i in range(1, 8):
                if column - i < 0:
                    break
                if self.board.board[row][column - i] is not None:
                    if self.board.player_check([row, column - i]) == 2:
                        column_upper = column - i
                        break
                    column_upper = column - i + 1
                    break

            for i in range(row_lower, row_upper + 1):
                resultList.append([i, column])

            for i in range(column_lower, column_upper + 1):
                resultList.append([row, i])

        elif self.chess.name == '車':
            potentialList = []
            row_upper, row_lower, column_upper, column_lower = row, row, column, column
            for i in range(1, 9):
                if row + i > 9:
                    break
                if self.board.board[row + i][column] is not None:
                    if self.board.player_check([row + i, column]) == 1:
                        row_upper = row + i
                        break
                    row_upper = row + i - 1
                    break
            for i in range(1, 9):
                if row - i < 0:
                    break
                if self.board.board[row - i][column] is not None:
                    if self.board.player_check([row - i, column]) == 1:
                        row_lower = row - i
                        break
                    row_lower = row - i + 1
                    break

            for i in range(1, 8):
                if column + i > 8:
                    break
                if self.board.board[row][column + i] is not None:
                    if self.board.player_check([row, column + i]) == 1:
                        column_upper = column + i
                        break
                    column_upper = column + i - 1
                    break

            for i in range(1, 8):
                if column - i < 0:
                    break
                if self.board.board[row][column - i] is not None:
                    if self.board.player_check([row, column - i]) == 1:
                        column_upper = column - i
                        break
                    column_upper = column - i + 1
                    break

            for i in range(row_lower,row_upper + 1):
                resultList.append([i, column])

            for i in range(column_lower, column_upper + 1):
                resultList.append([row,i])


        elif self.chess.name == '炮':
            '''
            can use the same way as Rook and then add the eating position
            '''
            row_upper, row_lower, column_upper, column_lower = row, row, column, column
            eat_row_upper, eat_row_lower, eat_column_upper, eat_column_lower = None, None, None, None
            Flag = False
            for i in range(1, 9):
                if row + i > 9:
                    if not Flag:
                        row_lower = 9
                    break
                if self.board.board[row + i][column] is not None and not Flag:
                    row_lower = row + i - 1
                    Flag = True
                    continue
                if Flag and self.board.board[row + i][column] is not None:
                    if self.board.player_check([row + i, column]) == 2:
                        eat_row_lower = row + i
                    break

            Flag = False
            for i in range(1, 9):
                if row - i < 0:
                    if not Flag:
                        row_upper = 0
                    break
                if self.board.board[row - i][column] is not None and not Flag:
                    row_upper = row - i + 1
                    Flag = True
                    continue
                if Flag and self.board.board[row - i][column] is not None:
                    if self.board.player_check([row - i, column]) == 2:
                        eat_row_upper = row - i
                    break

            Flag = False
            for i in range(1, 8):
                if column + i > 8:
                    if not Flag:
                        column_upper = 8
                    break
                if self.board.board[row][column + i] is not None and not Flag:
                    column_upper = column + i - 1
                    Flag = True
                    continue
                if Flag and self.board.board[row][column + i] is not None:
                    if self.board.player_check([row, column + i]) == 2:
                        eat_column_upper = column + i
                    break

            Flag = False
            for i in range(1, 8):
                if column - i < 0:
                    if not Flag:
                        column_lower = 0
                    break
                if self.board.board[row][column - i] is not None and not Flag:
                    column_lower = column - i + 1
                    Flag = True
                    continue
                if Flag and self.board.board[row][column - i] is not None:
                    if self.board.player_check([row, column - i]) == 2:
                        eat_column_lower = column - i
                    break

            for i in range(row_lower, row_upper + 1):
                resultList.append([i, column])

            for i in range(column_lower, column_upper + 1):
                resultList.append([row, i])

            if eat_column_lower != None:
                resultList.append([row, eat_column_lower])

            if eat_column_upper != None:
                resultList.append([row, eat_column_upper])

            if eat_row_upper != None:
                resultList.append([eat_row_upper, column])

            if eat_row_lower != None:
                resultList.append([eat_row_lower, column])

            resultList = [list(x) for x in set(tuple(x) for x in resultList)]


        elif self.chess.name == '砲':
            row_upper, row_lower, column_upper, column_lower = row, row, column, column
            eat_row_upper, eat_row_lower, eat_column_upper, eat_column_lower = None, None, None, None
            Flag = False
            for i in range(1, 9):
                if row + i > 9:
                    if not Flag:
                        row_upper = 9
                    break
                if self.board.board[row + i][column] is not None and not Flag:
                    row_upper = row + i - 1
                    Flag = True
                    continue
                if Flag and self.board.board[row + i][column] is not None:
                    if self.board.player_check([row + i, column]) == 1:
                        eat_row_upper = row + i
                    break

            Flag = False
            for i in range(1, 9):
                if row - i < 0:
                    if not Flag:
                        row_lower = 0
                    break
                if self.board.board[row - i][column] is not None and not Flag:
                    row_lower = row - i + 1
                    Flag = True
                    continue
                if Flag and self.board.board[row - i][column] is not None:
                    if self.board.player_check([row - i, column]) == 1:
                        eat_row_lower = row - i
                    break

            Flag = False
            for i in range(1, 8):
                if column + i > 8:
                    if not Flag:
                        column_upper = 8
                    break
                if self.board.board[row][column + i] is not None and not Flag:
                    column_upper = column + i - 1
                    Flag = True
                    continue
                if Flag and self.board.board[row][column + i] is not None:
                    if self.board.player_check([row, column + i]) == 1:
                        eat_column_upper = column + i
                    break

            Flag = False
            for i in range(1, 8):
                if column - i < 0:
                    if not Flag:
                        column_lower = 0
                    break
                if self.board.board[row][column - i] is not None and not Flag:
                    column_lower = column - i + 1
                    Flag = True
                    continue
                if Flag and self.board.board[row][column - i] is not None:
                    if self.board.player_check([row, column - i]) == 1:
                        eat_column_lower = column - i
                    break

            for i in range(row_lower, row_upper + 1):
                resultList.append([i, column])

            for i in range(column_lower, column_upper + 1):
                resultList.append([row, i])

            if eat_column_lower != None:
                resultList.append([row, eat_column_lower])

            if eat_column_upper != None:
                resultList.append([row, eat_column_upper])

            if eat_row_upper != None:
                resultList.append([eat_row_upper, column])

            if eat_row_lower != None:
                resultList.append([eat_row_lower, column])

            resultList = [list(x) for x in set(tuple(x) for x in resultList)]

        # Also the movement can't cause your Gerneral in dangers
        resultList = [item for item in resultList if item != self.chess.position]
        if check:
            resultList = self.dangerous_check(self.chess.position,resultList)
        self.chess.places = resultList
        return resultList


    def applyRules(self):
        row = self.chess.position[0]
        column = self.chess.position[1]
        if not self.board.blackchecking and not self.board.redchecking:
            self.board.redchecking = False
            self.board.blackchecking = False
            #record the current position of the chess
            #check the type of the chess
            resultList = self.moveList()
            # Test if this move cause a check on general
            for pos in resultList:
                if self.board.board[pos[0]][pos[1]] is None:
                    continue
                if (self.board.board[pos[0]][pos[1]].name == '帅' and self.board.player_check(pos) == 1):
                    self.board.redchecking = True #checking
                    break
                if (self.board.board[pos[0]][pos[1]].name == '将' and self.board.player_check(pos) == 2):
                    self.board.blackchecking = True #checking
                    break
        else:
            print("Check! Please respond")
            # deal with check now
            if self.board.redchecking:
                potentialList = [[row - 1, column], [row, column + 1], [row + 1, column], [row, column - 1]]
                resultList = self.checkBoundary(7, 9, 3, 5, potentialList)
                resultList = [list(x) for x in set(tuple(x) for x in resultList) if
                              self.board.board[x[0]][x[1]] is None or self.board.player_check(x) != 1]
            else:
                potentialList = [[row - 1, column], [row, column + 1], [row + 1, column], [row, column - 1]]
                resultList = self.checkBoundary(0, 2, 3, 5, potentialList)
                resultList = [list(x) for x in set(tuple(x) for x in resultList) if
                              self.board.board[x[0]][x[1]] is None or self.board.player_check(x) != 2]
        #self.chess.places = resultList
        return resultList

    def checkEnemy(self, position):
        """
        Check if the chess at the position is enemy or not.
        Return True if it is enemy, else return False.
        """
        if self.board.board[position[0]][position[1]] is None:
            return False
        elif self.board.board[position[0]][position[1]].player == self.chess.player:
            return False
        return True

    def checkBoundary(self, row_lower, row_upper, column_lower, column_upper, potentialList):
        """
        Check if the positions in potentialList are in the boundary.
        """
        result = []
        for position in potentialList:
            if row_lower <= position[0] <= row_upper and column_lower <= position[1] <= column_upper:
                result.append(position)
        return result

    def checkCannon(self, row_lower, row_upper, column_lower, column_upper, potentialList):
        row_lower -= 1
        while row_lower > 0:
            row_lower -= 1
            if self.checkEnemy([row_lower, self.chess.position[1]]) is True:
                potentialList.append([row_lower, self.chess.position[1]])
                break
        while row_upper < 9:
            row_upper += 1
            if self.checkEnemy([row_upper, self.chess.position[1]]):
                potentialList.append([row_upper, self.chess.position[1]])
                break
        while column_lower > 0:
            column_lower -= 1
            if self.checkEnemy([self.chess.position[0], column_lower]):
                potentialList.append([self.chess.position[0], column_lower])
                break
        while column_upper < 8:
            column_upper += 1
            if self.checkEnemy([self.chess.position[0], column_upper]):
                potentialList.append([self.chess.position[0], column_upper])
                break
        return potentialList

    def dangerous_check(self,chess_position, resultList):
        if self.board.board[chess_position[0]][chess_position[1]] is None:
            return resultList
        player = self.board.board[chess_position[0]][chess_position[1]].player
        ts = [i for i in resultList]
        if player.attribute == 1:
            ravel = Player('Test', 2)
            gerneralplace = self.board.redg.position
        else:
            ravel = Player('Test',1)
            gerneralplace = self.board.blackg.position

        for pos in resultList:
            # psudoupdates
            '''
            we can use undo opertaion which we also want to implements to do this
            '''
            temp = self.board.board[chess_position[0]][chess_position[1]]
            self.board.board[chess_position[0]][chess_position[1]] = None
            self.board.board[pos[0]][pos[1]] = temp
            self.board.moveList[tuple(chess_position)] = tuple(pos)
            ravel_move = list(self.board.all_movements(ravel).values())
            concat = []
            for item in ravel_move:
                for inner in item:
                    concat.append(inner)
            #check gerneral not been attacked
            #print(gerneralplace,ravel_move)
            if gerneralplace in concat:
                ts.remove(pos)
            self.board = self.board.one_step_undo()
            #gc.collect()
        return ts

def Rightformat(word):
    return True


def GameMain():
    '''
    Things GameMain should do:
    1. While not checkmate, keep the game running.
    2. Deal with any runtime error when game is running.
    3. If one player gives up, end the game immediately.
    4. If one player wants to undo one step, should able to undo it.
    '''
    pl1 = Player('red',1)
    pl2 = Player('black',2)
    nb = Board(pl1, pl2)
    #print(nb.all_movements(pl1))
    if True:
        nb.display()
        nb.update(pl1,(6,0),(5,0))
        nb.update(pl1,(5,0),(4,0))
        nb.update(pl1,(4,0),(3,0))
        nb.update(pl2,(0,0),(3,0))
        nb.update(pl1,(9,0),(3,0))
        nb.update(pl1,(7,1),(0,1))
        #nb.update(pl2,(2,1),(9,1)) #this is wrong and do nothing now
        nb.update(pl1,(9,2),(7,4))
        nb.update(pl1,(9,3),(8,4))
        nb.update(pl1,(9,1),(8,3))
        nb.update(pl1,(9,4),(9,3))
        #print(nb.all_movements(pl2))
        #nb.update(pl1,(8,3),(6,2)) #wrong cant eat yourself
        #nb.update(pl2,(0,3),(1,4)) #wrong cant make your Gerneral been checked
        nb.update(pl2,(0,4),(0,3))
        #nb.update(pl1,(8,3),(7,1)) #wrong, genreal can't meet
        #print(nb.all_movements(pl2))
        #print(nb.board[2][1].places) # should give original places which is wrong since this piece haven't moved before
        #nb.update(pl2,(2,1),(1,1))
        #nb.update(pl2,(2,1),(2,2))
        #print(nb.all_movements(pl2))
        #print(nb.board[1][1].places)
        #nb.update(pl2,(1,1),(1,7))
        #print(nb.board[1][7].places)
        #nb = nb.one_step_undo()

        nb.display()
        #nb.display()
    #print(nb.moveList)
    #print(os.getcwd())

    try:
        record = Path("./Records/record")
        record.resolve()
        num = open(record, "r").readline()
        num = int(num) + 1
    except FileNotFoundError:
        print("Record file messed up, Please run recovery program")
        exit(1)
    else:
        record.write_text(str(num))
        print(num)
    '''
    Each time the game starts, we will create a script and when the game
    ends, we will keep this script as data if Checkmate is in script, otherwise
    we will discard this(maybe pull back the file_name_number_counter)
    '''
    #new_script =
    print("Welcome to the world of BetaCome!")
    player1 = input("Player1 please enter your name: ")
    player2 = input("Player2 please enter your name: ")


GameMain()
