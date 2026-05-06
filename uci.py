import sys
from bitboards import Board
from search import Searcher
from move_encoding import move_to_uci
from moves import generate_legal_moves
from constants import WHITE
def get_normalized_fen(board):
    full_fen = board.to_fen()
    return ' '.join(full_fen.split()[:4])
def parse_time_to_ms(t_str):
    try:
        if isinstance(t_str, (int, float)):
            return int(t_str * 1000) if t_str < 10000 else int(t_str)
        s_str = str(t_str).strip()
        if ':' in s_str:
            parts = s_str.split(':')
            if len(parts) == 3:
                h, m, s = parts
                return int((int(h) * 3600 + int(m) * 60 + float(s)) * 1000)
            elif len(parts) == 2:
                m, s = parts
                return int((int(m) * 60 + float(s)) * 1000)
        return int(float(s_str))
    except:
        return 60000
def check_opening_book(board):
    normalized_fen = get_normalized_fen(board)
    if board.turn == WHITE:
        if normalized_fen == 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -':
            return 'd2d4'
    else:
        d5_responses = ['rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq -', 'rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R b KQkq -', 'rnbqkbnr/pppppppp/8/8/5P2/8/PPPPP1PP/RNBQKBNR b KQkq -']
        if normalized_fen in d5_responses:
            return 'd7d5'
        e5_responses = ['rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq -', 'rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq -']
        if normalized_fen in e5_responses:
            return 'e7e5'
    return None
def main():
    board = Board.from_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
    searcher = Searcher()
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        parts = line.strip().split()
        if not parts:
            continue
        command = parts[0]
        if command == 'uci':
            print('id name PureChess')
            print('id author User')
            print('uciok')
        elif command == 'isready':
            print('readyok')
        elif command == 'ucinewgame':
            board = Board.from_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        elif command == 'position':
            if 'startpos' in parts:
                board = Board.from_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
            elif 'fen' in parts:
                try:
                    idx = parts.index('fen')
                    board = Board.from_fen(' '.join(parts[idx + 1:idx + 7]))
                except:
                    pass
            if 'moves' in parts:
                moves = parts[parts.index('moves') + 1:]
                for m_uci in moves:
                    for move in generate_legal_moves(board):
                        if move_to_uci(move) == m_uci:
                            board.make_move(move)
                            break
        elif command == 'go':
            book_move = check_opening_book(board)
            if book_move:
                print(f'bestmove {book_move}')
                sys.stdout.flush()
                continue
            wtime = btime = 60000
            winc = binc = 0
            for i in range(len(parts) - 1):
                if parts[i] == 'wtime':
                    wtime = parse_time_to_ms(parts[i + 1])
                if parts[i] == 'btime':
                    btime = parse_time_to_ms(parts[i + 1])
                if parts[i] == 'winc':
                    winc = parse_time_to_ms(parts[i + 1])
                if parts[i] == 'binc':
                    binc = parse_time_to_ms(parts[i + 1])
            ms_left = wtime if board.turn == WHITE else btime
            inc_ms = winc if board.turn == WHITE else binc
            calculated_ms = ms_left / 40.0 + inc_ms * 0.8
            if ms_left < 5000:
                calculated_ms = min(calculated_ms, ms_left * 0.1)
            elif ms_left < 15000:
                calculated_ms = min(calculated_ms, ms_left * 0.2)
            calculated_ms = max(100, calculated_ms - 250)
            think_time = min(10.0, calculated_ms / 1000.0)
            think_time = max(0.1, think_time)
            print(f'info string budget {think_time:.3f}s bank {ms_left / 1000.0:.2f}s inc {inc_ms / 1000.0:.1f}s')
            sys.stdout.flush()
            try:
                best_move, score = searcher.search(board, think_time)
                if best_move:
                    print(f'bestmove {move_to_uci(best_move)}')
                else:
                    legal = generate_legal_moves(board)
                    print(f"bestmove {(move_to_uci(legal[0]) if legal else '0000')}")
            except Exception:
                legal = generate_legal_moves(board)
                print(f"bestmove {(move_to_uci(legal[0]) if legal else '0000')}")
        elif command == 'quit':
            break
        sys.stdout.flush()
if __name__ == '__main__':
    main()