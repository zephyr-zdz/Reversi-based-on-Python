import time
import csv
import random

direction = ((-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 1),
             (1, -1), (1, 0), (1, 1))


def init_board(n):
    board = [[{'state': '.', 'O': 0, 'X': 0, 'location': (i, j)} for j in range(0, n)] for i in range(0, n)]
    # O/X: 代表对应颜色落子的得分
    # score: 0代表没有可以翻的/已被占
    board[n // 2 - 1][n // 2 - 1]['state'] = 'O'
    board[n // 2][n // 2 - 1]['state'] = 'X'
    board[n // 2][n // 2]['state'] = 'O'
    board[n // 2 - 1][n // 2]['state'] = 'X'
    return board


def print_board(board):
    # 标题行
    print('   ', end='')
    for i in range(len(board)):
        print(chr(ord('a') + i), end='  ')
    print()

    # 1-n行
    index = 0
    for row in board:
        # 标题列
        print(chr(ord('a') + index), end='  ')
        for each in row:
            print(each['state'], end='  ')
        print()
        index += 1
    return 0


# 给一个方向打分(返回值)
def direction_score(board, position, color, arrow):
    row = position[0]
    col = position[1]
    score = 0
    while True:
        # 沿方向移动一格
        row += arrow[0]
        col += arrow[1]
        if 0 <= row < len(board) and 0 <= col < len(board):  # 还在表内
            if board[row][col]['state'] == '.':
                return 0
            if board[row][col]['state'] != color:
                score += 1  # 不同色 存着 等到找远端同色一起翻了
            elif board[row][col]['state'] == color:
                return score  # 同色 结算
        else:
            return 0  # 撞墙壁了 一个都翻不了


# 给棋盘上每一个格子打分(不返回值)
def score_board(board):
    for each in iterator_board(board):
        # XO
        row = each['location'][0]
        col = each['location'][1]
        each['X'] = 0
        each['O'] = 0
        if each['state'] != '.':
            continue
        # .
        for arrow in direction:
            each['X'] += direction_score(board, (row, col), 'X', arrow)
            each['O'] += direction_score(board, (row, col), 'O', arrow)


# 迭代按照先行后列抛出格子
def iterator_board(board):
    for row in board:
        for each in row:
            yield each


# 返回电脑执棋颜色（XO）
def init_game():
    xo = '/'
    while xo != 'X' and xo != 'O':
        xo = input('Computer plays (X/O) : ')
    return xo


# 电脑下棋，返回落子点
def computer_move(board, color):
    available = []
    max_score = 0
    for each in iterator_board(board):
        # 超过就刷新可选位置，相等就记录位置，没超过跳过
        if each[color] > max_score:
            max_score = each[color]
            available = [each['location']]  # 只记录位置
        elif each[color] == max_score and max_score > 0:
            available.append(each['location'])  # 只记录位置
        else:
            continue
    move = random.choice(available)
    print('Computer places', color, 'at', parse_move(move))
    return move


# 把人类的输入转变为(row,col)
def parse_to_move(move_string):
    return tuple([ord(x) - ord('a') for x in move_string])


def parse_move(move):
    return chr(move[0] + ord('a'))+chr(move[1] + ord('a'))   # string e.g: 'aa'


# 人类下棋，返回落子点
def human_move(color):
    hint = "Enter move for " + color + " (RowCol): "
    move = input(hint)
    return parse_to_move(move)


# 结果排序为：X, O
def calculate_board(board):
    x_count = 0
    o_count = 0
    for each in iterator_board(board):
        if each['state'] == 'X':
            x_count += 1
        if each['state'] == 'O':
            o_count += 1
    return x_count, o_count


# 检查棋盘是否还有可下的地方
def check_board(board):
    for each in iterator_board(board):
        if each['O'] + each['X'] > 0:
            return 1  # 有下棋的地方
    return 0  # 没有下棋的地方


# 检查棋盘是否还有可下的地方（某一颜色的）
def has_valid_move_board(board, color):
    for each in iterator_board(board):
        if each[color] > 0:
            return 1  # 有下棋的地方（某一颜色）
    return 0  # 没有下棋的地方（某一颜色）


# 翻面 不返回值
def flip(board, move):
    row = move[0]
    col = move[1]
    color = board[row][col]['state']
    for arrow in direction:
        direction_flip(board, move, color, arrow)


def direction_flip(board, position, color, arrow):
    row = position[0]
    col = position[1]
    to_change = []
    while True:
        # 沿方向移动一格
        row += arrow[0]
        col += arrow[1]
        if 0 <= row < len(board) and 0 <= col < len(board):  # 还在表内
            if board[row][col]['state'] == '.':
                return 0
            if board[row][col]['state'] != color:
                to_change.append(board[row][col]['location'])  # 不同色 存着 等到找远端同色一起翻了
            elif board[row][col]['state'] == color:
                for i in to_change:
                    board[i[0]][i[1]]['state'] = color
                return 0  # 同色 结算
        else:
            return 0  # 撞墙壁了 一个都翻不了


# 下棋 不返回值
def move_board(board, move, color):
    row = move[0]
    col = move[1]
    board[row][col]['state'] = color  # 先落子
    flip(board, move)  # 再翻面
    score_board(board)  # 下棋翻面一定要结算


def move_valid(board, human_move_attempt, color):
    row = human_move_attempt[0]
    col = human_move_attempt[1]
    if board[row][col][color] > 0:
        return 1  # 是有效的下棋
    return 0  # 是无效的下棋


def start_game(computer_color, board):
    human_color = 'O' if computer_color == 'X' else 'X'

    # 打印棋盘
    print_board(board)

    # 初始化棋盘打分
    score_board(board)

    # 若电脑先手，就先走一步
    if computer_color == 'X':
        move_board(board, computer_move(board, computer_color), computer_color)
    print_board(board)
    move = 1  # 0表示电脑，1表示人
    while check_board(board):
        if move == 0:
            # 电脑轮次，认为电脑不会下出无效位置
            if has_valid_move_board(board, computer_color):
                move_board(board, computer_move(board, computer_color), computer_color)
            else:
                print(computer_color, 'player has no valid move.')
        else:
            # 人的轮次，有可能是无效的
            if has_valid_move_board(board, human_color):
                human_move_attempt = human_move(human_color)
                if move_valid(board, human_move_attempt, human_color):
                    move_board(board, human_move_attempt, human_color)
                else:
                    print_board(board)
                    print('Invalid move.')
                    print('Game over.')
                    print(computer_color, 'player wins.')
                    return (-1, 0) if human_color == 'X' else (0, -1)  # 将人判负
            else:
                print(human_color, 'player has no valid move.')
        print_board(board)
        move = 1 - move  # 人机交换

    # 游戏结束
    print_board(board)
    print('Both players have no valid move.')
    print('Game over.')

    # 结算
    board_result = calculate_board(board)
    print('X : O = ', board_result[0], ':', board_result[1])
    if board_result[0] == board_result[1]:
        print('Draw.')
    elif board_result[0] > board_result[1]:
        print('X player wins.')
    else:
        print('O player wins.')

    return board_result


def log(start_time, duration, length, computer_color, result):
    size = str(length) + '*' + str(length)
    start_time = time.strftime("%Y%m%d %H:%M:%S", time.localtime(start_time))

    if result[0] >= 0 and result[1] >= 0:
        to_result = str(result[0]) + ' to ' + str(result[1])
    else:
        to_result = 'Computer gives up.' if (computer_color == 'X') == (result[0] == -1) else 'Human gives up.'

    row = [start_time, duration, size,
           'computer' if computer_color == 'X' else 'human',
           'computer' if computer_color == 'O' else 'human',
           to_result]

    f = open('Reversi.csv', 'a', newline='', encoding='utf8')
    with f:
        writer = csv.writer(f)
        writer.writerow(row)
    f.close()


if __name__ == '__main__':
    # 初始化
    size = 0
    while not (4 <= size <= 26 and size % 2 == 0):
        size = int(input('Enter the board dimension: '))
    main_board = init_board(size)
    computer_color = init_game()

    # 开始计时
    start_time = time.time()

    # 开始游戏
    result = start_game(computer_color, main_board)

    # 结束计时
    stop_time = time.time()
    duration = int(stop_time - start_time)
    input()
    # 记录结果
    log(start_time, duration, size, computer_color, result)
