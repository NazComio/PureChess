import sys
import os
from bitboards import Board
from search import Searcher, _full_score, _fast_eval, _nnue_output, resize_tt
from move_encoding import move_to_uci
from moves import generate_legal_moves
from constants import WHITE, BLACK
def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
resize_tt(256)
def get_normalized_fen(board):
    full_fen = board.to_fen()
    return ' '.join(full_fen.split()[:4])
def check_opening_book(board):
    normalized_fen = get_normalized_fen(board)
    book = {
        'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -': 'e2e4',
        'rnbqkbnr/pppppppp/8/8/8/P7/1PPPPPPP/RNBQKBNR b KQkq -': 'd7d5',
        'rnbqkbnr/pppppppp/8/8/8/1P6/P1PPPPPP/RNBQKBNR b KQkq -': 'e7e5',
        'rnbqkbnr/pppppppp/8/8/8/2P5/PP1PPPPP/RNBQKBNR b KQkq -': 'e7e5',
        'rnbqkbnr/pppppppp/8/8/8/3P4/PPP1PPPP/RNBQKBNR b KQkq -': 'd7d5',
        'rnbqkbnr/pppppppp/8/8/8/4P3/PPPP1PPP/RNBQKBNR b KQkq -': 'd7d5',
        'rnbqkbnr/pppppppp/8/8/8/5P2/PPPPP1PP/RNBQKBNR b KQkq -': 'e7e5',
        'rnbqkbnr/pppppppp/8/8/8/6P1/PPPPPP1P/RNBQKBNR b KQkq -': 'e7e5',
        'rnbqkbnr/pppppppp/8/8/8/7P/PPPPPPP1/RNBQKBNR b KQkq -': 'd7d5',
        'rnbqkbnr/pppppppp/8/8/P7/8/1PPPPPPP/RNBQKBNR b KQkq -': 'd7d5',
        'rnbqkbnr/pppppppp/8/8/1P6/8/P1PPPPPP/RNBQKBNR b KQkq -': 'c7c6',
        'rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq -': 'e7e5',
        'rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq -': 'd7d5',
        'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq -': 'e2e6',
        'rnbqkbnr/pppppppp/8/8/5P2/8/PPPPP1PP/RNBQKBNR b KQkq -': 'd7d5',
        'rnbqkbnr/pppppppp/8/8/6P1/8/PPPPPP1P/RNBQKBNR b KQkq -': 'b8c6',
        'rnbqkbnr/pppppppp/8/8/7P/8/PPPPPPP1/RNBQKBNR b KQkq -': 'e7e5',
        'r1bqkbnr/pppppppp/n7/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -': 'g1f3',
        'r1bqkbnr/pppppppp/2n7/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -': 'd7d5',
        'rnbqkb1r/pppppppp/5n2/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -': 'd7d5',
        'rnbqkb1r/pppppppp/7n/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq -': 'e7e5',
        'rnbqkbnr/1ppppppp/p7/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -': 'd2d4',
        'rnbqkbnr/p1pppppp/1p6/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -': 'b1c3',
        'rnbqkbnr/pp1ppppp/2p5/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -': 'd2d4',
        'rnbqkbnr/ppp1pppp/3p4/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -': 'd2d4',
        'rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -': 'g1f3',
        'rnbqkbnr/ppppp1pp/5p2/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -': 'b1c3',
        'rnbqkbnr/pppppp1p/6p1/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -': 'g1f3',
        'rnbqkbnr/ppppppp1/7p/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -': 'd2d4',
        'rnbqkbnr/1ppppppp/8/p7/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -': 'g1f3',
        'rnbqkbnr/p1pppppp/8/1p6/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -': 'f1b5',
        'rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -': 'b1c3',
        'rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -': 'e4d5',
        'rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -': 'b1c3',
        'rnbqkbnr/ppppp1pp/8/5p2/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -': 'e4f5',
        'rnbqkbnr/pppppp1p/8/6p1/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -': 'd2d4',
        'rnbqkbnr/ppppppp1/8/7p/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -': 'd2d4',
        'r1bqkbnr/pppppppp/n7/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -': 'g1f3',
        'r1bqkbnr/pppppppp/2n7/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -': 'd2d4',
        'rnbqkb1r/pppppppp/5n2/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -': 'e4e5',
        'rnbqkb1r/pppppppp/7n/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -': 'g1f3',
    }
    return book.get(normalized_fen, None)
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
def main():
    board = Board.from_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
    searcher = Searcher()
    use_book = True
    while True:
        line = sys.stdin.readline()
        if not line: break
        parts = line.strip().split()
        if not parts: continue
        command = parts[0]
        if command == 'uci':
            print('id name PureChess')
            print('id author User')
            print('option name Hash type spin default 256 min 1 max 16384')
            print('option name OwnBook type check default true')
            print('uciok')
        elif command == 'isready':
            print('readyok')
        elif command == 'setoption':
            try:
                name_idx  = parts.index('name')  + 1
                value_idx = parts.index('value') + 1
                opt_name  = ' '.join(parts[name_idx:value_idx - 1]).strip().lower()
                opt_value = parts[value_idx]
                if opt_name == 'hash':
                    mb = max(1, min(16384, int(opt_value)))
                    resize_tt(mb)
                    searcher = Searcher()
                elif opt_name == 'ownbook':
                    use_book = (opt_value.lower() == 'true')
            except (ValueError, IndexError):
                pass
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
            book_move = check_opening_book(board) if use_book else None
            if book_move:
                print(f'bestmove {book_move}')
                sys.stdout.flush()
                continue
            wtime = btime = 60000
            winc = binc = 0
            for i in range(len(parts) - 1):
                if parts[i] == 'wtime': wtime = parse_time_to_ms(parts[i + 1])
                if parts[i] == 'btime': btime = parse_time_to_ms(parts[i + 1])
                if parts[i] == 'winc': winc = parse_time_to_ms(parts[i + 1])
                if parts[i] == 'binc': binc = parse_time_to_ms(parts[i + 1])
            ms_left = wtime if board.turn == WHITE else btime
            inc_ms = winc if board.turn == WHITE else binc
            divisor = 8 if ms_left < 3000 else 15 if ms_left < 10000 else 20 if ms_left < 30000 else 25 if ms_left < 60000 else 30
            calculated_ms = min(ms_left / divisor + inc_ms * 0.85, ms_left * 0.40)
            think_time = min(15.0, max(200, calculated_ms) / 1000.0)
            print(f'info string budget {think_time:.3f}s')
            sys.stdout.flush()
            try:
                best_move, score = searcher.search(board, think_time)
                print(f'bestmove {(move_to_uci(best_move) if best_move else "0000")}')
            except Exception:
                legal = generate_legal_moves(board)
                print(f"bestmove {(move_to_uci(legal[0]) if legal else '0000')}")
        elif command == 'eval':
            acc      = _full_score(board)
            nnue_raw = _nnue_output(acc)
            nnue_stm = nnue_raw if board.turn == WHITE else -nnue_raw
            print(f'NNUE Score: {nnue_stm/100:.2f}')
        elif command == 'quit':
            break
        sys.stdout.flush()
if __name__ == '__main__':
    main()
