from constants import P, N, B, R, Q, K, WHITE, BLACK, FULL_BOARD, CASTLE_WK, CASTLE_WQ, CASTLE_BK, CASTLE_BQ, CASTLE_ROOK_FROM, CASTLE_ROOK_TO, CASTLE_RIGHTS_MASK
from move_encoding import move_type, promo_piece, MT_KING_CASTLE, MT_QUEEN_CASTLE, MT_EP_CAPTURE, FLAG_PROMO
class Board:
    __slots__ = ('pieces', 'occ', 'all_occ', 'turn', 'castling', 'ep_sq', 'halfmove', 'fullmove', '_undo', 'piece_at')
    def __init__(self):
        self.pieces = [[0] * 6, [0] * 6]
        self.occ = [0, 0]
        self.all_occ = 0
        self.turn = WHITE
        self.castling = 0
        self.ep_sq = -1
        self.halfmove = 0
        self.fullmove = 1
        self._undo = []
        self.piece_at = [-1] * 64
    @classmethod
    def from_start(cls):
        b = cls()
        b.set_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        return b
    @classmethod
    def from_fen(cls, fen: str):
        b = cls()
        b.set_fen(fen)
        return b
    def set_fen(self, fen: str):
        parts = fen.split()
        self.pieces = [[0] * 6, [0] * 6]
        self.occ = [0, 0]
        self.all_occ = 0
        self.piece_at = [-1] * 64
        piece_map = {'P': (WHITE, P), 'N': (WHITE, N), 'B': (WHITE, B), 'R': (WHITE, R), 'Q': (WHITE, Q), 'K': (WHITE, K), 'p': (BLACK, P), 'n': (BLACK, N), 'b': (BLACK, B), 'r': (BLACK, R), 'q': (BLACK, Q), 'k': (BLACK, K)}
        rank = 7
        file = 0
        for ch in parts[0]:
            if ch == '/':
                rank -= 1
                file = 0
            elif ch.isdigit():
                file += int(ch)
            else:
                c, pc = piece_map[ch]
                sq = rank * 8 + file
                bb = 1 << sq
                self.pieces[c][pc] |= bb
                self.occ[c] |= bb
                self.all_occ |= bb
                self.piece_at[sq] = pc
                file += 1
        self.turn = WHITE if parts[1] == 'w' else BLACK
        cr = parts[2]
        self.castling = 0
        if 'K' in cr:
            self.castling |= CASTLE_WK
        if 'Q' in cr:
            self.castling |= CASTLE_WQ
        if 'k' in cr:
            self.castling |= CASTLE_BK
        if 'q' in cr:
            self.castling |= CASTLE_BQ
        ep = parts[3]
        if ep == '-':
            self.ep_sq = -1
        else:
            f = ord(ep[0]) - ord('a')
            r = int(ep[1]) - 1
            self.ep_sq = r * 8 + f
        self.halfmove = int(parts[4]) if len(parts) > 4 else 0
        self.fullmove = int(parts[5]) if len(parts) > 5 else 1
        self._undo = []
    def to_fen(self) -> str:
        piece_chars = [['P', 'N', 'B', 'R', 'Q', 'K'], ['p', 'n', 'b', 'r', 'q', 'k']]
        rows = []
        for rank in range(7, -1, -1):
            row = ''
            empty = 0
            for file in range(8):
                sq = rank * 8 + file
                found = False
                for c in (WHITE, BLACK):
                    for pc in range(6):
                        if self.pieces[c][pc] >> sq & 1:
                            if empty:
                                row += str(empty)
                                empty = 0
                            row += piece_chars[c][pc]
                            found = True
                            break
                    if found:
                        break
                if not found:
                    empty += 1
            if empty:
                row += str(empty)
            rows.append(row)
        board_str = '/'.join(rows)
        turn_str = 'w' if self.turn == WHITE else 'b'
        cr = ''
        if self.castling & CASTLE_WK:
            cr += 'K'
        if self.castling & CASTLE_WQ:
            cr += 'Q'
        if self.castling & CASTLE_BK:
            cr += 'k'
        if self.castling & CASTLE_BQ:
            cr += 'q'
        if not cr:
            cr = '-'
        if self.ep_sq == -1:
            ep_str = '-'
        else:
            ep_str = 'abcdefgh'[self.ep_sq % 8] + str(self.ep_sq // 8 + 1)
        return f'{board_str} {turn_str} {cr} {ep_str} {self.halfmove} {self.fullmove}'
    def _put_piece(self, color: int, pc: int, sq: int):
        bb = 1 << sq
        self.pieces[color][pc] |= bb
        self.occ[color] |= bb
        self.all_occ |= bb
        self.piece_at[sq] = pc
    def _remove_piece(self, color: int, pc: int, sq: int):
        bb = 1 << sq
        nbb = ~bb & FULL_BOARD
        self.pieces[color][pc] &= nbb
        self.occ[color] &= nbb
        self.all_occ &= nbb
        self.piece_at[sq] = -1
    def _move_piece(self, color: int, pc: int, fr: int, to: int):
        bb_fr = 1 << fr
        bb_to = 1 << to
        toggle = bb_fr | bb_to
        self.pieces[color][pc] ^= toggle
        self.occ[color] ^= toggle
        self.all_occ ^= toggle
        self.piece_at[fr] = -1
        self.piece_at[to] = pc
    def make_move(self, move: int):
        self._undo.append((move, self.castling, self.ep_sq, self.halfmove))
        us = self.turn
        them = us ^ 1
        mt = move_type(move)
        fr = move & 63
        to = move >> 6 & 63
        pc = move >> 16 & 7
        self.castling &= CASTLE_RIGHTS_MASK[fr] & CASTLE_RIGHTS_MASK[to]
        prev_ep = self.ep_sq
        self.ep_sq = -1
        self.halfmove += 1
        if mt == 0:
            self._move_piece(us, pc, fr, to)
            if pc == P:
                self.halfmove = 0
        elif mt == 1 << 12:
            self._move_piece(us, pc, fr, to)
            self.ep_sq = fr + to >> 1
            self.halfmove = 0
        elif mt == MT_KING_CASTLE:
            rf = CASTLE_ROOK_FROM[CASTLE_WK if us == WHITE else CASTLE_BK]
            rt = CASTLE_ROOK_TO[CASTLE_WK if us == WHITE else CASTLE_BK]
            self._move_piece(us, K, fr, to)
            self._move_piece(us, R, rf, rt)
        elif mt == MT_QUEEN_CASTLE:
            rf = CASTLE_ROOK_FROM[CASTLE_WQ if us == WHITE else CASTLE_BQ]
            rt = CASTLE_ROOK_TO[CASTLE_WQ if us == WHITE else CASTLE_BQ]
            self._move_piece(us, K, fr, to)
            self._move_piece(us, R, rf, rt)
        elif mt == MT_EP_CAPTURE:
            cap_sq = prev_ep + (-8 if us == WHITE else 8)
            self._remove_piece(them, P, cap_sq)
            self._move_piece(us, P, fr, to)
            self.halfmove = 0
        elif move & FLAG_PROMO:
            cap = move >> 19 & 7
            if move & 4 << 12:
                self._remove_piece(them, cap, to)
                self.halfmove = 0
            promo_pc = promo_piece(move)
            self._remove_piece(us, P, fr)
            self._put_piece(us, promo_pc, to)
            self.halfmove = 0
        else:
            cap = move >> 19 & 7
            self._remove_piece(them, cap, to)
            self._move_piece(us, pc, fr, to)
            self.halfmove = 0
        if us == BLACK:
            self.fullmove += 1
        self.turn = them
    def unmake_move(self, move: int):
        move, self.castling, self.ep_sq, self.halfmove = self._undo.pop()
        self.turn ^= 1
        us = self.turn
        them = us ^ 1
        mt = move_type(move)
        fr = move & 63
        to = move >> 6 & 63
        pc = move >> 16 & 7
        if us == BLACK:
            self.fullmove -= 1
        if mt == 0 or mt == 1 << 12:
            self._move_piece(us, pc, to, fr)
        elif mt == MT_KING_CASTLE:
            rf = CASTLE_ROOK_FROM[CASTLE_WK if us == WHITE else CASTLE_BK]
            rt = CASTLE_ROOK_TO[CASTLE_WK if us == WHITE else CASTLE_BK]
            self._move_piece(us, K, to, fr)
            self._move_piece(us, R, rt, rf)
        elif mt == MT_QUEEN_CASTLE:
            rf = CASTLE_ROOK_FROM[CASTLE_WQ if us == WHITE else CASTLE_BQ]
            rt = CASTLE_ROOK_TO[CASTLE_WQ if us == WHITE else CASTLE_BQ]
            self._move_piece(us, K, to, fr)
            self._move_piece(us, R, rt, rf)
        elif mt == MT_EP_CAPTURE:
            cap_sq = self.ep_sq + (-8 if us == WHITE else 8)
            self._move_piece(us, P, to, fr)
            self._put_piece(them, P, cap_sq)
        elif move & FLAG_PROMO:
            promo_pc = promo_piece(move)
            cap = move >> 19 & 7
            self._remove_piece(us, promo_pc, to)
            self._put_piece(us, P, fr)
            if move & 4 << 12:
                self._put_piece(them, cap, to)
        else:
            cap = move >> 19 & 7
            self._move_piece(us, pc, to, fr)
            self._put_piece(them, cap, to)
    def piece_color_at(self, sq: int):
        bb = 1 << sq
        if self.occ[WHITE] & bb:
            return (WHITE, self.piece_at[sq])
        if self.occ[BLACK] & bb:
            return (BLACK, self.piece_at[sq])
        return (-1, -1)
    def __repr__(self) -> str:
        chars = ['.'] * 64
        piece_chars = [['P', 'N', 'B', 'R', 'Q', 'K'], ['p', 'n', 'b', 'r', 'q', 'k']]
        for c in (WHITE, BLACK):
            for pc in range(6):
                bb = self.pieces[c][pc]
                while bb:
                    lsb = bb & -bb
                    sq = lsb.bit_length() - 1
                    chars[sq] = piece_chars[c][pc]
                    bb &= bb - 1
        rows = []
        for rank in range(7, -1, -1):
            row = f'{rank + 1} '
            for file in range(8):
                row += chars[rank * 8 + file] + ' '
            rows.append(row)
        rows.append('  a b c d e f g h')
        turn_str = 'White' if self.turn == WHITE else 'Black'
        rows.append(f'Turn: {turn_str} | Castling: {self.castling:04b} | EP: {self.ep_sq}')
        return '\n'.join(rows)