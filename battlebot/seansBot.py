import random
import requests
import sys

BASE_URL = "http://battleship.inseng.net/games"
COLUMNS = "ABCDEFGHIJ"
left = 'left'
down = 'down'

pos1 = {
    'carrierCell': 'A4',
    'carrierDir': 'down',
    'batCell': 'C2',
    'batDir': 'left',
    'desCell': 'F9',
    'desDir': 'left',
    'cruCell': 'D7',
    'cruDir': 'down',
    'subCell': 'H10',
    'subDir': 'left'
}


def getGame():
    r = requests.post(BASE_URL)
    data = r.json()
    assert data['state'] == 'CREATED', 'New game is not in created state!'
    print("=== Starting Game ===")
    print(data)
    return data


def addPlayer(game_id, name, position, match = None ):
    data = {
        'name': name,
        'carrierCell': position['carrierCell'],
        'carrierDirection': position['carrierDir'],
        'battleshipCell': position['batCell'],
        'battleshipDirection': position['batDir'],
        'destroyerCell': position['desCell'],
        'destroyerDirection': position['desDir'],
        'cruiserCell': position['cruCell'],
        'cruiserDirection': position['cruDir'],
        'submarineCell': position['subCell'],
        'submarineDirection': position['subDir'],
    }

    if match:
        data['match'] = match

    print("=== Adding Player ===")
    print("Data sent:")
    print(data)
    r = requests.post(BASE_URL + '/' + game_id + '/players', data=data)
    results = r.json()
   # assert results['state'] == 'IN_PROGRESS', 'Started game is not in progress!'
    print("Adding Player Response:")
    print(results)
    return results


def move(game_id, token, cellTuple):
    url = BASE_URL + '/%s/moves' % game_id
    headers = {
        'X-Token': token
    }
    data = {
        'move': cellToStr(cellTuple)
    }
    r = requests.post(url, data=data, headers=headers)

    print("Move submitted")
    print("Move cell: {}".format(cellTuple))
    print("Status Code: {}".format(r.status_code))
    print("Response JSON: {}".format(r.json()))
    return r.json()


def check_hit(cell, board):
    (col, row) = cell
    hit_val =  board[row][col]
    if hit_val == 1:
        return True
    elif hit_val == 0:
        return False
    else:
        exit("There was an error")


def play_board(token, id, name):
    evenCells = [(col, row) for col in range(1,10,2) for row in range(0,9,2)]
    oddCells =  [(col, row) for col in range(0,9,2) for row in range(1,10,2)]
    validCells = evenCells + oddCells
    move_data = None
    cell = None

    while len(validCells) != 0:
        while(cell == None and len(validCells) != 0):
            cell = validCells.pop(random.randint(0, len(validCells) - 1))
            if check_if_tried(cell, move_data, name):
                print("Hit used cell at {}, trying again".format(cell))
                cell = None

        if cell:
            print("Cell Selected: Cell {}".format(cell))

            move_data = move(id, token, cell)
            hit = check_hit(cell, move_data['currentPlayer']['moves'])
            if hit:
                try_target(id, token, cell, move_data, name)
            cell = None


    remainingCells = [(col, row)for col in range(0,10) for row in range(0,10)]
    cell = None
    while (len(remainingCells) != 0):
        cell = remainingCells.pop(random.randint(0, len(remainingCells) - 1))
        if check_if_tried(cell, move_data, name):
            cell = None

        if cell:
            move_data = move(id, token, cell)


def try_target(id, token, cell, move_data, name, orientation = None):
    target_cells = get_target_spots(cell, move_data, orientation, name)
    print("=== Cells being targeted from ({}) ===".format(cell))
    print(target_cells)
    target_orientation = orientation
    for target_cell in target_cells:
        return_data = move(id, token, target_cell)
        if check_hit(target_cell,return_data['currentPlayer']['moves']):
            if cell[0] == target_cell[0]:
                target_orientation = 'vertical'
                print("Orientation defined as vertical")
            elif cell[1] == target_cell[1]:
                target_orientation = 'horizontal'
                print("Orientation defined as horizontal")
            try_target(id, token, target_cell, return_data, name, target_orientation)


def get_target_spots(cell, move_data, orientation, name):
    target_spots = []
    if orientation == None:
        target_spots.extend([
            (cell[0] + 1, cell[1]),
            (cell[0] - 1, cell[1]),
            (cell[0], cell[1] + 1),
            (cell[0], cell[1] - 1)
        ])
    elif orientation == 'horizontal':
        target_spots.extend([
            (cell[0] + 1, cell[1]),
            (cell[0] - 1, cell[1])
        ])
    elif orientation == 'vertical':
        target_spots.extend([
            (cell[0], cell[1] + 1),
            (cell[0], cell[1] - 1)
        ])
    else:
        print("ERROR: orientation came as: {}".format(orientation))
        print("Just adding all of the spots")
        target_spots.extend([
            (cell[0] + 1, cell[1]),
            (cell[0] - 1, cell[1]),
            (cell[0], cell[1] + 1),
            (cell[0], cell[1] - 1)
        ])

    target_spots = [x for x in target_spots if validMove(x) and not check_if_tried(x, move_data, name)]
    return target_spots


def check_if_tried(cell, data, name):
    if data == None:
        return False

    board = data['currentPlayer']['moves']
    hit_val = board[cell[1]][cell[0]]
    if hit_val == 1:
        return True
    elif hit_val == 0:
        return True
    else:
        return False


def cellToStr(column, row):
    return chr(64 + column + 1) + str(row + 1)

def cellToStr(tuple):
    return chr(64 + tuple[0] + 1) + str(tuple[1] + 1)

def cellToTuple(cell):
    col = ord(cell[0]) - 64
    row = int(cell[1:len(cell)])
    return(col, row)

def validMove(cell):
    (col, row) = cell
    if col < 0 or col > 9:
        return False
    elif row < 0 or row > 9:
        return False
    else:
        return True


if __name__ == "__main__":

    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print("USAGE: bot.py player_name [id] [token]")

    name = sys.argv[1]
    if len(sys.argv) == 2:
        start_game_data = getGame()
        game_data = addPlayer(start_game_data['id'], name, pos1)
        id = game_data['id']
        token = game_data['currentPlayer']['token']
        play_board(token, id, name)

    if len(sys.argv) == 3:
        game_id = sys.argv[2]
        game_data = addPlayer(game_id, name, pos1)
        id = game_data['id']
        token = game_data['currentPlayer']['token']
        play_board(token, id, name)

    if len(sys.argv) == 4:
        game_id = sys.argv[2]
        token = sys.argv[3]
        play_board(token, game_id, name)
