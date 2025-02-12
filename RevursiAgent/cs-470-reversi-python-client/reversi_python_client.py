import reversi
import sys

if __name__ == '__main__':
    server_address = sys.argv[1]
    bot_move_number = int(sys.argv[2])
    max_depth = int(sys.argv[3])
    w_1 = float(sys.argv[4])
    w_2 = float(sys.argv[5])
    w_3 = float(sys.argv[6])
    w_4 = float(sys.argv[7])
    w_5 = float(sys.argv[8])
    w_6 = float(sys.argv[9])

    print(f"w_1: {w_1}, w_2: {w_2}, w_3: {w_3}, w_4: {w_4}, w_5: {w_5}, w_6: {w_6}")

    reversi_game = reversi.ReversiGame(server_address, bot_move_number, max_depth, w_1, w_2, w_3, w_4, w_5, w_6)
    reversi_game.play()


