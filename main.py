from __future__ import annotations
import sys
import time, random

P = 0
N = 1
B = 2
R = 3
Q = 4
K = 5
WHITE = 0
BLACK = 1
A1, B1, C1, D1, E1, F1, G1, H1 = (0, 1, 2, 3, 4, 5, 6, 7)
A2, B2, C2, D2, E2, F2, G2, H2 = (8, 9, 10, 11, 12, 13, 14, 15)
A3, B3, C3, D3, E3, F3, G3, H3 = (16, 17, 18, 19, 20, 21, 22, 23)
A4, B4, C4, D4, E4, F4, G4, H4 = (24, 25, 26, 27, 28, 29, 30, 31)
A5, B5, C5, D5, E5, F5, G5, H5 = (32, 33, 34, 35, 36, 37, 38, 39)
A6, B6, C6, D6, E6, F6, G6, H6 = (40, 41, 42, 43, 44, 45, 46, 47)
A7, B7, C7, D7, E7, F7, G7, H7 = (48, 49, 50, 51, 52, 53, 54, 55)
A8, B8, C8, D8, E8, F8, G8, H8 = (56, 57, 58, 59, 60, 61, 62, 63)
SQUARE_NAMES = ['a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1', 'a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2', 'a3', 'b3', 'c3', 'd3', 'e3', 'f3', 'g3', 'h3', 'a4', 'b4', 'c4', 'd4', 'e4', 'f4', 'g4', 'h4', 'a5', 'b5', 'c5', 'd5', 'e5', 'f5', 'g5', 'h5', 'a6', 'b6', 'c6', 'd6', 'e6', 'f6', 'g6', 'h6', 'a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7', 'a8', 'b8', 'c8', 'd8', 'e8', 'f8', 'g8', 'h8']
FILE_A = 72340172838076673
FILE_B = FILE_A << 1
FILE_C = FILE_A << 2
FILE_D = FILE_A << 3
FILE_E = FILE_A << 4
FILE_F = FILE_A << 5
FILE_G = FILE_A << 6
FILE_H = FILE_A << 7
RANK_1 = 255
RANK_2 = RANK_1 << 8
RANK_3 = RANK_1 << 16
RANK_4 = RANK_1 << 24
RANK_5 = RANK_1 << 32
RANK_6 = RANK_1 << 40
RANK_7 = RANK_1 << 48
RANK_8 = RANK_1 << 56
NOT_FILE_A = ~FILE_A & 18446744073709551615
NOT_FILE_H = ~FILE_H & 18446744073709551615
NOT_FILE_AB = ~(FILE_A | FILE_B) & 18446744073709551615
NOT_FILE_GH = ~(FILE_G | FILE_H) & 18446744073709551615
FULL_BOARD = 18446744073709551615
BB_SQUARES = [1 << sq for sq in range(64)]
def _build_knight_attacks():
    table = [0] * 64
    for sq in range(64):
        bb = 1 << sq
        attacks = bb << 17 & NOT_FILE_A
        attacks |= bb << 15 & NOT_FILE_H
        attacks |= bb << 10 & NOT_FILE_AB
        attacks |= bb << 6 & NOT_FILE_GH
        attacks |= bb >> 17 & NOT_FILE_H
        attacks |= bb >> 15 & NOT_FILE_A
        attacks |= bb >> 10 & NOT_FILE_GH
        attacks |= bb >> 6 & NOT_FILE_AB
        table[sq] = attacks & FULL_BOARD
    return table
KNIGHT_ATTACKS = _build_knight_attacks()
def _build_king_attacks():
    table = [0] * 64
    for sq in range(64):
        bb = 1 << sq
        attacks = bb << 8
        attacks |= bb >> 8
        attacks |= bb << 1 & NOT_FILE_A
        attacks |= bb >> 1 & NOT_FILE_H
        attacks |= bb << 9 & NOT_FILE_A
        attacks |= bb >> 9 & NOT_FILE_H
        attacks |= bb << 7 & NOT_FILE_H
        attacks |= bb >> 7 & NOT_FILE_A
        table[sq] = attacks & FULL_BOARD
    return table
KING_ATTACKS = _build_king_attacks()
def _build_pawn_attacks():
    white = [0] * 64
    black = [0] * 64
    for sq in range(64):
        bb = 1 << sq
        white[sq] = (bb << 9 & NOT_FILE_A | bb << 7 & NOT_FILE_H) & FULL_BOARD
        black[sq] = (bb >> 7 & NOT_FILE_A | bb >> 9 & NOT_FILE_H) & FULL_BOARD
    return [white, black]
PAWN_ATTACKS = _build_pawn_attacks()
def _build_rays():
    rays = [[0] * 64 for _ in range(8)]
    for sq in range(64):
        f, r = (sq % 8, sq // 8)
        for i in range(r + 1, 8):
            rays[0][sq] |= 1 << i * 8 + f
        for i in range(1, min(8 - f, 8 - r)):
            rays[1][sq] |= 1 << sq + 9 * i
        for i in range(f + 1, 8):
            rays[2][sq] |= 1 << r * 8 + i
        for i in range(1, min(8 - f, r + 1)):
            rays[3][sq] |= 1 << sq - 7 * i
        for i in range(r - 1, -1, -1):
            rays[4][sq] |= 1 << i * 8 + f
        for i in range(1, min(f + 1, r + 1)):
            rays[5][sq] |= 1 << sq - 9 * i
        for i in range(f - 1, -1, -1):
            rays[6][sq] |= 1 << r * 8 + i
        for i in range(1, min(f + 1, 8 - r)):
            rays[7][sq] |= 1 << sq + 7 * i
    return rays
RAYS = _build_rays()
RAY_N = RAYS[0]
RAY_NE = RAYS[1]
RAY_E = RAYS[2]
RAY_SE = RAYS[3]
RAY_S = RAYS[4]
RAY_SW = RAYS[5]
RAY_W = RAYS[6]
RAY_NW = RAYS[7]
def _build_between():
    between = [[0] * 64 for _ in range(64)]
    for sq1 in range(64):
        for d in range(8):
            ray = RAYS[d][sq1]
            bb = ray
            while bb:
                lsb = bb & -bb
                sq2 = lsb.bit_length() - 1
                between[sq1][sq2] = RAYS[d][sq1] ^ RAYS[d][sq2] ^ lsb
                bb &= bb - 1
    return between
BETWEEN = _build_between()
def _build_lines():
    lines = [[0] * 64 for _ in range(64)]
    for sq1 in range(64):
        for d in range(8):
            ray = RAYS[d][sq1]
            bb = ray
            while bb:
                lsb = bb & -bb
                sq2 = lsb.bit_length() - 1
                opp = (d + 4) % 8
                lines[sq1][sq2] = RAYS[d][sq1] | RAYS[opp][sq1] | 1 << sq1
                bb &= bb - 1
    return lines
LINE = _build_lines()
CASTLE_WK = 1
CASTLE_WQ = 2
CASTLE_BK = 4
CASTLE_BQ = 8
CASTLE_EMPTY = {CASTLE_WK: 1 << F1 | 1 << G1, CASTLE_WQ: 1 << B1 | 1 << C1 | 1 << D1, CASTLE_BK: 1 << F8 | 1 << G8, CASTLE_BQ: 1 << B8 | 1 << C8 | 1 << D8}
CASTLE_SAFE = {CASTLE_WK: 1 << E1 | 1 << F1 | 1 << G1, CASTLE_WQ: 1 << E1 | 1 << D1 | 1 << C1, CASTLE_BK: 1 << E8 | 1 << F8 | 1 << G8, CASTLE_BQ: 1 << E8 | 1 << D8 | 1 << C8}
CASTLE_ROOK_FROM = {CASTLE_WK: H1, CASTLE_WQ: A1, CASTLE_BK: H8, CASTLE_BQ: A8}
CASTLE_ROOK_TO = {CASTLE_WK: F1, CASTLE_WQ: D1, CASTLE_BK: F8, CASTLE_BQ: D8}
CASTLE_RIGHTS_MASK = [15] * 64
CASTLE_RIGHTS_MASK[E1] &= ~(CASTLE_WK | CASTLE_WQ)
CASTLE_RIGHTS_MASK[H1] &= ~CASTLE_WK
CASTLE_RIGHTS_MASK[A1] &= ~CASTLE_WQ
CASTLE_RIGHTS_MASK[E8] &= ~(CASTLE_BK | CASTLE_BQ)
CASTLE_RIGHTS_MASK[H8] &= ~CASTLE_BK
CASTLE_RIGHTS_MASK[A8] &= ~CASTLE_BQ
MT_QUIET = 0 << 12
MT_DOUBLE_PUSH = 1 << 12
MT_KING_CASTLE = 2 << 12
MT_QUEEN_CASTLE = 3 << 12
MT_CAPTURE = 4 << 12
MT_EP_CAPTURE = 5 << 12
MT_KNIGHT_PROMO = 8 << 12
MT_BISHOP_PROMO = 9 << 12
MT_ROOK_PROMO = 10 << 12
MT_QUEEN_PROMO = 11 << 12
MT_KNIGHT_PROMO_C = 12 << 12
MT_BISHOP_PROMO_C = 13 << 12
MT_ROOK_PROMO_C = 14 << 12
MT_QUEEN_PROMO_C = 15 << 12
PROMO_TYPES = (MT_KNIGHT_PROMO, MT_BISHOP_PROMO, MT_ROOK_PROMO, MT_QUEEN_PROMO)
PROMO_CAPTURE_TYPES = (MT_KNIGHT_PROMO_C, MT_BISHOP_PROMO_C, MT_ROOK_PROMO_C, MT_QUEEN_PROMO_C)
FROM_MASK = 63
TO_MASK = 63 << 6
TYPE_MASK = 15 << 12
PIECE_MASK = 7 << 16
CAP_MASK = 7 << 19
FLAG_CAPTURE = 4 << 12
FLAG_PROMO = 8 << 12
FLAG_EP = 5 << 12
FLAG_CASTLE_K = 2 << 12
FLAG_CASTLE_Q = 3 << 12
def encode_move(from_sq: int, to_sq: int, move_type: int, piece: int=0, captured: int=0) -> int:
    return from_sq | to_sq << 6 | move_type | piece << 16 | captured << 19
def from_sq(move: int) -> int:
    return move & 63
def to_sq(move: int) -> int:
    return move >> 6 & 63
def move_type(move: int) -> int:
    return move & TYPE_MASK
def piece(move: int) -> int:
    return move >> 16 & 7
def captured(move: int) -> int:
    return move >> 19 & 7
def is_capture(move: int) -> bool:
    return bool(move & FLAG_CAPTURE)
def is_promotion(move: int) -> bool:
    return bool(move & FLAG_PROMO)
def is_ep(move: int) -> bool:
    return move & TYPE_MASK == MT_EP_CAPTURE
def is_castle(move: int) -> bool:
    mt = move & TYPE_MASK
    return mt == MT_KING_CASTLE or mt == MT_QUEEN_CASTLE
_PROMO_PIECE = [1, 2, 3, 4]
def promo_piece(move: int) -> int:
    return _PROMO_PIECE[move >> 12 & 3]
_FILE_CHARS = 'abcdefgh'
_RANK_CHARS = '12345678'
_PROMO_CHARS = {1: 'n', 2: 'b', 3: 'r', 4: 'q'}
def move_to_uci(move: int) -> str:
    f = move & 63
    t = move >> 6 & 63
    uci = _FILE_CHARS[f % 8] + _RANK_CHARS[f // 8] + _FILE_CHARS[t % 8] + _RANK_CHARS[t // 8]
    if move & FLAG_PROMO:
        uci += _PROMO_CHARS.get(promo_piece(move), '')
    return uci
_P16 = P << 16
_N16 = N << 16
_B16 = B << 16
_R16 = R << 16
_Q16 = Q << 16
_K16 = K << 16
_KA = KNIGHT_ATTACKS
_KING = KING_ATTACKS
_PA = PAWN_ATTACKS
_LINE = LINE
_BET = BETWEEN
_BB = BB_SQUARES
_RAYS = RAYS
_FULL = FULL_BOARD
_NFA = NOT_FILE_A
_NFH = NOT_FILE_H
_R1 = RANK_1
_R2 = RANK_2
_R3 = RANK_3
_R6 = RANK_6
_R7 = RANK_7
_R8 = RANK_8
_CE_WK = CASTLE_EMPTY[CASTLE_WK]
_CE_WQ = CASTLE_EMPTY[CASTLE_WQ]
_CE_BK = CASTLE_EMPTY[CASTLE_BK]
_CE_BQ = CASTLE_EMPTY[CASTLE_BQ]
_MT_CAP = MT_CAPTURE
_MT_Q = MT_QUIET
_MT_DP = MT_DOUBLE_PUSH
_MT_KC = MT_KING_CASTLE
_MT_QC = MT_QUEEN_CASTLE
_MT_EP = MT_EP_CAPTURE
_NKP = MT_KNIGHT_PROMO
_BKP = MT_BISHOP_PROMO
_RKP = MT_ROOK_PROMO
_QKP = MT_QUEEN_PROMO
_NKPC = MT_KNIGHT_PROMO_C
_BKPC = MT_BISHOP_PROMO_C
_RKPC = MT_ROOK_PROMO_C
_QKPC = MT_QUEEN_PROMO_C
def _build_slider_tables():
    def _bref(sq, occ):
        r = _BB[sq]
        a = 0
        for ray, neg in ((_RAYS[1][sq], False), (_RAYS[7][sq], False), (_RAYS[5][sq], True), (_RAYS[3][sq], True)):
            o = occ & ray
            if neg:
                if o:
                    msb = 1 << o.bit_length() - 1
                    a |= ray ^ ray & msb - 1
                else:
                    a |= ray
            else:
                a |= (o - 2 * r ^ o) & ray
        return a
    def _rref(sq, occ):
        r = _BB[sq]
        a = 0
        for ray, neg in ((_RAYS[0][sq], False), (_RAYS[2][sq], False), (_RAYS[4][sq], True), (_RAYS[6][sq], True)):
            o = occ & ray
            if neg:
                if o:
                    msb = 1 << o.bit_length() - 1
                    a |= ray ^ ray & msb - 1
                else:
                    a |= ray
            else:
                a |= (o - 2 * r ^ o) & ray
        return a
    def _bmask(sq):
        mask = 0
        f, r = (sq % 8, sq // 8)
        for df, dr in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            cf, cr = (f + df, r + dr)
            while 1 <= cf <= 6 and 1 <= cr <= 6:
                mask |= 1 << cr * 8 + cf
                cf += df
                cr += dr
        return mask
    def _rmask(sq):
        mask = 0
        f, r = (sq % 8, sq // 8)
        for i in range(f + 1, 7):
            mask |= 1 << r * 8 + i
        for i in range(1, f):
            mask |= 1 << r * 8 + i
        for i in range(r + 1, 7):
            mask |= 1 << i * 8 + f
        for i in range(1, r):
            mask |= 1 << i * 8 + f
        return mask
    bm = [_bmask(sq) for sq in range(64)]
    rm = [_rmask(sq) for sq in range(64)]
    bt = []
    rt = []
    for sq in range(64):
        mask = bm[sq]
        d = {0: _bref(sq, 0)}
        sub = mask
        while sub:
            d[sub] = _bref(sq, sub)
            sub = sub - 1 & mask
        bt.append(d)
    for sq in range(64):
        mask = rm[sq]
        d = {0: _rref(sq, 0)}
        sub = mask
        while sub:
            d[sub] = _rref(sq, sub)
            sub = sub - 1 & mask
        rt.append(d)
    return (bm, rm, bt, rt)
_BISHOP_MASKS, _ROOK_MASKS, _BISHOP_TABLE, _ROOK_TABLE = _build_slider_tables()
def bishop_attacks(sq, occ):
    return _BISHOP_TABLE[sq][occ & _BISHOP_MASKS[sq]]
def rook_attacks(sq, occ):
    return _ROOK_TABLE[sq][occ & _ROOK_MASKS[sq]]
def queen_attacks(sq, occ):
    return _BISHOP_TABLE[sq][occ & _BISHOP_MASKS[sq]] | _ROOK_TABLE[sq][occ & _ROOK_MASKS[sq]]
def is_attacked(sq, attacker_color, board):
    occ = board.all_occ
    pieces = board.pieces[attacker_color]
    defender = attacker_color ^ 1
    if _PA[defender][sq] & pieces[P]:
        return True
    if _KA[sq] & pieces[N]:
        return True
    if _KING[sq] & pieces[K]:
        return True
    diag = pieces[B] | pieces[Q]
    if diag and _BISHOP_TABLE[sq][occ & _BISHOP_MASKS[sq]] & diag:
        return True
    orth = pieces[R] | pieces[Q]
    if orth and _ROOK_TABLE[sq][occ & _ROOK_MASKS[sq]] & orth:
        return True
    return False
def is_attacked_no_king(sq, attacker, board, occ):
    pieces = board.pieces[attacker]
    defender = attacker ^ 1
    if _PA[defender][sq] & pieces[P]:
        return True
    if _KA[sq] & pieces[N]:
        return True
    if _KING[sq] & pieces[K]:
        return True
    diag = pieces[B] | pieces[Q]
    if diag and _BISHOP_TABLE[sq][occ & _BISHOP_MASKS[sq]] & diag:
        return True
    orth = pieces[R] | pieces[Q]
    if orth and _ROOK_TABLE[sq][occ & _ROOK_MASKS[sq]] & orth:
        return True
    return False
def attacks_to(sq, occ, board):
    return _PA[BLACK][sq] & board.pieces[WHITE][P] | _PA[WHITE][sq] & board.pieces[BLACK][P] | _KA[sq] & (board.pieces[WHITE][N] | board.pieces[BLACK][N]) | _KING[sq] & (board.pieces[WHITE][K] | board.pieces[BLACK][K]) | _BISHOP_TABLE[sq][occ & _BISHOP_MASKS[sq]] & (board.pieces[WHITE][B] | board.pieces[BLACK][B] | board.pieces[WHITE][Q] | board.pieces[BLACK][Q]) | _ROOK_TABLE[sq][occ & _ROOK_MASKS[sq]] & (board.pieces[WHITE][R] | board.pieces[BLACK][R] | board.pieces[WHITE][Q] | board.pieces[BLACK][Q])
def get_attack_info(board, us, king_sq):
    them = us ^ 1
    occ = board.all_occ
    our_occ = board.occ[us]
    pt = board.pieces[them]
    pN = pt[N]
    pB = pt[B]
    pR = pt[R]
    pQ = pt[Q]
    diag = pB | pQ
    orth = pR | pQ
    pinned = 0
    checkers = _PA[us][king_sq] & pt[P] | _KA[king_sq] & pN
    rays = _RAYS
    for d, slider in ((0, orth), (2, orth), (1, diag), (7, diag)):
        ray = rays[d][king_sq]
        if ray and slider:
            bl = ray & occ
            if bl:
                f = bl & -bl
                if f & slider:
                    checkers |= f
                elif f & our_occ:
                    be = ray & ~((f << 1) - 1) & ~f & occ
                    if be and be & -be & slider:
                        pinned |= f
    for d, slider in ((4, orth), (6, orth), (5, diag), (3, diag)):
        ray = rays[d][king_sq]
        if ray and slider:
            bl = ray & occ
            if bl:
                f = 1 << bl.bit_length() - 1
                if f & slider:
                    checkers |= f
                elif f & our_occ:
                    fs = f.bit_length() - 1
                    bb2 = ray & (1 << fs) - 1 & occ
                    if bb2 and 1 << bb2.bit_length() - 1 & slider:
                        pinned |= f
    return (checkers, pinned)
def get_checkers(board, us, king_sq):
    them = us ^ 1
    occ = board.all_occ
    p = board.pieces[them]
    return _PA[us][king_sq] & p[P] | _KA[king_sq] & p[N] | bishop_attacks(king_sq, occ) & (p[B] | p[Q]) | rook_attacks(king_sq, occ) & (p[R] | p[Q])
def get_pinned_pieces(board, us, king_sq):
    _, pinned = get_attack_info(board, us, king_sq)
    return pinned
def _gen_pawn_moves(board, us, them, pinned, king_sq, check_mask, ml):
    pawns = board.pieces[us][P]
    if not pawns:
        return
    occ = board.all_occ
    tocc = board.occ[them]
    pat = board.piece_at
    ep_sq = board.ep_sq
    LINE = _LINE
    BB = _BB
    NFA = _NFA
    NFH = _NFH
    FULL = _FULL
    NKP = _NKP
    BKP = _BKP
    RKP = _RKP
    QKP = _QKP
    NKPC = _NKPC
    BKPC = _BKPC
    RKPC = _RKPC
    QKPC = _QKPC
    append = ml.append
    if us == WHITE:
        single = pawns << 8 & ~occ & FULL
        double = (single & _R3) << 8 & ~occ
        cl = pawns << 7 & NFH & tocc
        cr = pawns << 9 & NFA & tocc
        ep_bb = BB[ep_sq] if ep_sq != -1 else 0
        el = pawns << 7 & NFH & ep_bb
        er = pawns << 9 & NFA & ep_bb
        fwd = 8
        fwd2 = 16
        cl_off = 7
        cr_off = 9
        promo = _R8
    else:
        single = pawns >> 8 & ~occ
        double = (single & _R6) >> 8 & ~occ
        cl = pawns >> 9 & NFH & tocc
        cr = pawns >> 7 & NFA & tocc
        ep_bb = BB[ep_sq] if ep_sq != -1 else 0
        el = pawns >> 9 & NFH & ep_bb
        er = pawns >> 7 & NFA & ep_bb
        fwd = -8
        fwd2 = -16
        cl_off = -9
        cr_off = -7
        promo = _R1
    bb = single & ~promo & check_mask
    while bb:
        lsb = bb & -bb
        bb ^= lsb
        to = lsb.bit_length() - 1
        fr = to - fwd
        if BB[fr] & pinned and (not LINE[king_sq][fr] >> to & 1):
            continue
        append(fr | to << 6 | _MT_Q | _P16)
    bb = double & check_mask
    while bb:
        lsb = bb & -bb
        bb ^= lsb
        to = lsb.bit_length() - 1
        fr = to - fwd2
        if BB[fr] & pinned and (not LINE[king_sq][fr] >> to & 1):
            continue
        append(fr | to << 6 | _MT_DP | _P16)
    bb = single & promo & check_mask
    while bb:
        lsb = bb & -bb
        bb ^= lsb
        to = lsb.bit_length() - 1
        fr = to - fwd
        if BB[fr] & pinned and (not LINE[king_sq][fr] >> to & 1):
            continue
        base = fr | to << 6 | _P16
        append(base | NKP)
        append(base | BKP)
        append(base | RKP)
        append(base | QKP)
    bb = cl & check_mask
    while bb:
        lsb = bb & -bb
        bb ^= lsb
        to = lsb.bit_length() - 1
        fr = to - cl_off
        if BB[fr] & pinned and (not LINE[king_sq][fr] >> to & 1):
            continue
        cap_pc = pat[to]
        if lsb & promo:
            base = fr | to << 6 | _P16 | cap_pc << 19
            append(base | NKPC)
            append(base | BKPC)
            append(base | RKPC)
            append(base | QKPC)
        else:
            append(fr | to << 6 | _MT_CAP | _P16 | cap_pc << 19)
    bb = cr & check_mask
    while bb:
        lsb = bb & -bb
        bb ^= lsb
        to = lsb.bit_length() - 1
        fr = to - cr_off
        if BB[fr] & pinned and (not LINE[king_sq][fr] >> to & 1):
            continue
        cap_pc = pat[to]
        if lsb & promo:
            base = fr | to << 6 | _P16 | cap_pc << 19
            append(base | NKPC)
            append(base | BKPC)
            append(base | RKPC)
            append(base | QKPC)
        else:
            append(fr | to << 6 | _MT_CAP | _P16 | cap_pc << 19)
    if el or er:
        p_them = board.pieces[them]
        pB_t = p_them[B]
        pR_t = p_them[R]
        pQ_t = p_them[Q]
        BT = _BISHOP_TABLE
        RT = _ROOK_TABLE
        BMK = _BISHOP_MASKS
        RMK = _ROOK_MASKS
        BB2 = _BB
        for bb2, off in ((el, cl_off), (er, cr_off)):
            while bb2:
                lsb = bb2 & -bb2
                bb2 ^= lsb
                to = lsb.bit_length() - 1
                fr = to - off
                cap_sq = to - fwd
                occ2 = occ ^ BB2[fr] ^ BB2[cap_sq] | BB2[to]
                diag2 = pB_t | pQ_t
                if diag2 and BT[king_sq][occ2 & BMK[king_sq]] & diag2:
                    continue
                orth2 = pR_t | pQ_t
                if orth2 and RT[king_sq][occ2 & RMK[king_sq]] & orth2:
                    continue
                append(fr | to << 6 | _MT_EP | _P16)
def _gen_knight_moves(board, us, them, pinned, check_mask, ml):
    knights = board.pieces[us][N] & ~pinned
    if not knights:
        return
    tocc = board.occ[them]
    nocc = board.occ[us]
    pat = board.piece_at
    KA = _KA
    MT_CAP = _MT_CAP
    MT_Q = _MT_Q
    N16 = _N16
    append = ml.append
    while knights:
        lsb = knights & -knights
        knights ^= lsb
        fr = lsb.bit_length() - 1
        targets = KA[fr] & ~nocc & check_mask
        caps = targets & tocc
        quiets = targets ^ caps
        while caps:
            alb = caps & -caps
            caps ^= alb
            to = alb.bit_length() - 1
            append(fr | to << 6 | MT_CAP | N16 | pat[to] << 19)
        while quiets:
            alb = quiets & -quiets
            quiets ^= alb
            append(fr | alb.bit_length() - 1 << 6 | MT_Q | N16)
def _gen_bishop_moves(board, us, them, pinned, king_sq, check_mask, ml):
    bishops = board.pieces[us][B]
    if not bishops:
        return
    tocc = board.occ[them]
    nocc = board.occ[us]
    occ = board.all_occ
    pat = board.piece_at
    LINE = _LINE
    BT = _BISHOP_TABLE
    BMK = _BISHOP_MASKS
    MT_CAP = _MT_CAP
    MT_Q = _MT_Q
    B16 = _B16
    append = ml.append
    while bishops:
        lsb = bishops & -bishops
        bishops ^= lsb
        fr = lsb.bit_length() - 1
        attacks = BT[fr][occ & BMK[fr]] & ~nocc
        if lsb & pinned:
            attacks &= LINE[king_sq][fr]
        attacks &= check_mask
        caps = attacks & tocc
        quiets = attacks ^ caps
        while caps:
            alb = caps & -caps
            caps ^= alb
            to = alb.bit_length() - 1
            append(fr | to << 6 | MT_CAP | B16 | pat[to] << 19)
        while quiets:
            alb = quiets & -quiets
            quiets ^= alb
            append(fr | alb.bit_length() - 1 << 6 | MT_Q | B16)
def _gen_rook_moves(board, us, them, pinned, king_sq, check_mask, ml):
    rooks = board.pieces[us][R]
    if not rooks:
        return
    tocc = board.occ[them]
    nocc = board.occ[us]
    occ = board.all_occ
    pat = board.piece_at
    LINE = _LINE
    RT = _ROOK_TABLE
    RMK = _ROOK_MASKS
    MT_CAP = _MT_CAP
    MT_Q = _MT_Q
    R16 = _R16
    append = ml.append
    while rooks:
        lsb = rooks & -rooks
        rooks ^= lsb
        fr = lsb.bit_length() - 1
        attacks = RT[fr][occ & RMK[fr]] & ~nocc
        if lsb & pinned:
            attacks &= LINE[king_sq][fr]
        attacks &= check_mask
        caps = attacks & tocc
        quiets = attacks ^ caps
        while caps:
            alb = caps & -caps
            caps ^= alb
            to = alb.bit_length() - 1
            append(fr | to << 6 | MT_CAP | R16 | pat[to] << 19)
        while quiets:
            alb = quiets & -quiets
            quiets ^= alb
            append(fr | alb.bit_length() - 1 << 6 | MT_Q | R16)
def _gen_queen_moves(board, us, them, pinned, king_sq, check_mask, ml):
    queens = board.pieces[us][Q]
    if not queens:
        return
    tocc = board.occ[them]
    nocc = board.occ[us]
    occ = board.all_occ
    pat = board.piece_at
    LINE = _LINE
    BT = _BISHOP_TABLE
    BMK = _BISHOP_MASKS
    RT = _ROOK_TABLE
    RMK = _ROOK_MASKS
    MT_CAP = _MT_CAP
    MT_Q = _MT_Q
    Q16 = _Q16
    append = ml.append
    while queens:
        lsb = queens & -queens
        queens ^= lsb
        fr = lsb.bit_length() - 1
        attacks = (BT[fr][occ & BMK[fr]] | RT[fr][occ & RMK[fr]]) & ~nocc
        if lsb & pinned:
            attacks &= LINE[king_sq][fr]
        attacks &= check_mask
        caps = attacks & tocc
        quiets = attacks ^ caps
        while caps:
            alb = caps & -caps
            caps ^= alb
            to = alb.bit_length() - 1
            append(fr | to << 6 | MT_CAP | Q16 | pat[to] << 19)
        while quiets:
            alb = quiets & -quiets
            quiets ^= alb
            append(fr | alb.bit_length() - 1 << 6 | MT_Q | Q16)
def _gen_king_moves(board, us, them, king_sq, check_mask, ml):
    tocc = board.occ[them]
    nocc = board.occ[us]
    occ = board.all_occ
    pat = board.piece_at
    p = board.pieces[them]
    PA = _PA
    KA = _KA
    KING = _KING
    BB = _BB
    BT = _BISHOP_TABLE
    BMK = _BISHOP_MASKS
    RT = _ROOK_TABLE
    RMK = _ROOK_MASKS
    MT_CAP = _MT_CAP
    MT_Q = _MT_Q
    defender = them ^ 1
    pP = p[P]
    pN = p[N]
    pB = p[B]
    pR = p[R]
    pQ = p[Q]
    pK = p[K]
    diag_att = pB | pQ
    orth_att = pR | pQ
    occ_nk = occ ^ BB[king_sq]
    attacks = KING[king_sq] & ~nocc
    append = ml.append
    while attacks:
        alb = attacks & -attacks
        attacks ^= alb
        to = alb.bit_length() - 1
        if PA[defender][to] & pP:
            continue
        if KA[to] & pN:
            continue
        if KING[to] & pK:
            continue
        if diag_att and BT[to][occ_nk & BMK[to]] & diag_att:
            continue
        if orth_att and RT[to][occ_nk & RMK[to]] & orth_att:
            continue
        if alb & tocc:
            append(king_sq | to << 6 | MT_CAP | _K16 | pat[to] << 19)
        else:
            append(king_sq | to << 6 | MT_Q | _K16)
    if check_mask != _FULL:
        return
    cr = board.castling
    if us == WHITE:
        if cr & 1 and (not occ & _CE_WK):
            ok = True
            for sq in (4, 5, 6):
                if PA[defender][sq] & pP or KA[sq] & pN or KING[sq] & pK:
                    ok = False
                    break
                if diag_att and BT[sq][occ & BMK[sq]] & diag_att:
                    ok = False
                    break
                if orth_att and RT[sq][occ & RMK[sq]] & orth_att:
                    ok = False
                    break
            if ok:
                append(king_sq | 6 << 6 | _MT_KC | _K16)
        if cr & 2 and (not occ & _CE_WQ):
            ok = True
            for sq in (4, 3, 2):
                if PA[defender][sq] & pP or KA[sq] & pN or KING[sq] & pK:
                    ok = False
                    break
                if diag_att and BT[sq][occ & BMK[sq]] & diag_att:
                    ok = False
                    break
                if orth_att and RT[sq][occ & RMK[sq]] & orth_att:
                    ok = False
                    break
            if ok:
                append(king_sq | 2 << 6 | _MT_QC | _K16)
    else:
        if cr & 4 and (not occ & _CE_BK):
            ok = True
            for sq in (60, 61, 62):
                if PA[defender][sq] & pP or KA[sq] & pN or KING[sq] & pK:
                    ok = False
                    break
                if diag_att and BT[sq][occ & BMK[sq]] & diag_att:
                    ok = False
                    break
                if orth_att and RT[sq][occ & RMK[sq]] & orth_att:
                    ok = False
                    break
            if ok:
                append(king_sq | 62 << 6 | _MT_KC | _K16)
        if cr & 8 and (not occ & _CE_BQ):
            ok = True
            for sq in (60, 59, 58):
                if PA[defender][sq] & pP or KA[sq] & pN or KING[sq] & pK:
                    ok = False
                    break
                if diag_att and BT[sq][occ & BMK[sq]] & diag_att:
                    ok = False
                    break
                if orth_att and RT[sq][occ & RMK[sq]] & orth_att:
                    ok = False
                    break
            if ok:
                append(king_sq | 58 << 6 | _MT_QC | _K16)
def _gen_king_captures(board, us, them, king_sq, ml):
    tocc = board.occ[them]
    occ = board.all_occ
    pat = board.piece_at
    p = board.pieces[them]
    PA = _PA
    KA = _KA
    KING = _KING
    BB = _BB
    BT = _BISHOP_TABLE
    BMK = _BISHOP_MASKS
    RT = _ROOK_TABLE
    RMK = _ROOK_MASKS
    defender = them ^ 1
    pP = p[P]
    pN = p[N]
    pB = p[B]
    pR = p[R]
    pQ = p[Q]
    pK = p[K]
    diag_att = pB | pQ
    orth_att = pR | pQ
    occ_nk = occ ^ BB[king_sq]
    attacks = KING[king_sq] & tocc
    append = ml.append
    while attacks:
        alb = attacks & -attacks
        attacks ^= alb
        to = alb.bit_length() - 1
        if PA[defender][to] & pP:
            continue
        if KA[to] & pN:
            continue
        if KING[to] & pK:
            continue
        if diag_att and BT[to][occ_nk & BMK[to]] & diag_att:
            continue
        if orth_att and RT[to][occ_nk & RMK[to]] & orth_att:
            continue
        append(king_sq | to << 6 | _MT_CAP | _K16 | pat[to] << 19)
def _gen_pawn_captures(board, us, them, pinned, king_sq, check_mask, ml):
    pawns = board.pieces[us][P]
    if not pawns:
        return
    occ = board.all_occ
    tocc = board.occ[them]
    pat = board.piece_at
    ep_sq = board.ep_sq
    LINE = _LINE
    BB = _BB
    NFA = _NFA
    NFH = _NFH
    NKP = _NKP
    BKP = _BKP
    RKP = _RKP
    QKP = _QKP
    NKPC = _NKPC
    BKPC = _BKPC
    RKPC = _RKPC
    QKPC = _QKPC
    append = ml.append
    if us == WHITE:
        single = pawns << 8 & ~occ & _FULL
        cl = pawns << 7 & NFH & tocc
        cr = pawns << 9 & NFA & tocc
        ep_bb = BB[ep_sq] if ep_sq != -1 else 0
        el = pawns << 7 & NFH & ep_bb
        er = pawns << 9 & NFA & ep_bb
        fwd = 8
        cl_off = 7
        cr_off = 9
        promo = _R8
    else:
        single = pawns >> 8 & ~occ
        cl = pawns >> 9 & NFH & tocc
        cr = pawns >> 7 & NFA & tocc
        ep_bb = BB[ep_sq] if ep_sq != -1 else 0
        el = pawns >> 9 & NFH & ep_bb
        er = pawns >> 7 & NFA & ep_bb
        fwd = -8
        cl_off = -9
        cr_off = -7
        promo = _R1
    bb = single & promo & check_mask
    while bb:
        lsb = bb & -bb
        bb ^= lsb
        to = lsb.bit_length() - 1
        fr = to - fwd
        if BB[fr] & pinned and (not LINE[king_sq][fr] >> to & 1):
            continue
        base = fr | to << 6 | _P16
        append(base | NKP)
        append(base | BKP)
        append(base | RKP)
        append(base | QKP)
    bb = cl & check_mask
    while bb:
        lsb = bb & -bb
        bb ^= lsb
        to = lsb.bit_length() - 1
        fr = to - cl_off
        if BB[fr] & pinned and (not LINE[king_sq][fr] >> to & 1):
            continue
        cap_pc = pat[to]
        if lsb & promo:
            base = fr | to << 6 | _P16 | cap_pc << 19
            append(base | NKPC)
            append(base | BKPC)
            append(base | RKPC)
            append(base | QKPC)
        else:
            append(fr | to << 6 | _MT_CAP | _P16 | cap_pc << 19)
    bb = cr & check_mask
    while bb:
        lsb = bb & -bb
        bb ^= lsb
        to = lsb.bit_length() - 1
        fr = to - cr_off
        if BB[fr] & pinned and (not LINE[king_sq][fr] >> to & 1):
            continue
        cap_pc = pat[to]
        if lsb & promo:
            base = fr | to << 6 | _P16 | cap_pc << 19
            append(base | NKPC)
            append(base | BKPC)
            append(base | RKPC)
            append(base | QKPC)
        else:
            append(fr | to << 6 | _MT_CAP | _P16 | cap_pc << 19)
    if el or er:
        p_them = board.pieces[them]
        pB_t = p_them[B]
        pR_t = p_them[R]
        pQ_t = p_them[Q]
        BT = _BISHOP_TABLE
        RT = _ROOK_TABLE
        BMK = _BISHOP_MASKS
        RMK = _ROOK_MASKS
        BB2 = _BB
        for bb2, off in ((el, cl_off), (er, cr_off)):
            while bb2:
                lsb = bb2 & -bb2
                bb2 ^= lsb
                to = lsb.bit_length() - 1
                fr = to - off
                cap_sq = to - fwd
                occ2 = occ ^ BB2[fr] ^ BB2[cap_sq] | BB2[to]
                diag2 = pB_t | pQ_t
                if diag2 and BT[king_sq][occ2 & BMK[king_sq]] & diag2:
                    continue
                orth2 = pR_t | pQ_t
                if orth2 and RT[king_sq][occ2 & RMK[king_sq]] & orth2:
                    continue
                append(fr | to << 6 | _MT_EP | _P16)
def generate_legal_moves(board):
    us = board.turn
    them = us ^ 1
    ml = []
    king_bb = board.pieces[us][K]
    if not king_bb:
        return ml
    king_sq = king_bb.bit_length() - 1
    checkers, pinned = get_attack_info(board, us, king_sq)
    if not checkers:
        check_mask = _FULL
    elif checkers & checkers - 1:
        _gen_king_moves(board, us, them, king_sq, _FULL, ml)
        return ml
    else:
        checker_sq = checkers.bit_length() - 1
        check_mask = checkers | _BET[king_sq][checker_sq]
    _gen_king_moves(board, us, them, king_sq, check_mask, ml)
    _gen_pawn_moves(board, us, them, pinned, king_sq, check_mask, ml)
    _gen_knight_moves(board, us, them, pinned, check_mask, ml)
    _gen_bishop_moves(board, us, them, pinned, king_sq, check_mask, ml)
    _gen_rook_moves(board, us, them, pinned, king_sq, check_mask, ml)
    _gen_queen_moves(board, us, them, pinned, king_sq, check_mask, ml)
    return ml
def generate_legal_moves_ex(board):
    us = board.turn
    them = us ^ 1
    ml = []
    king_bb = board.pieces[us][K]
    if not king_bb:
        return (ml, 0, False)
    king_sq = king_bb.bit_length() - 1
    checkers, pinned = get_attack_info(board, us, king_sq)
    in_check = bool(checkers)
    if not checkers:
        check_mask = _FULL
    elif checkers & checkers - 1:
        _gen_king_moves(board, us, them, king_sq, _FULL, ml)
        return (ml, checkers, True)
    else:
        checker_sq = checkers.bit_length() - 1
        check_mask = checkers | _BET[king_sq][checker_sq]
    _gen_king_moves(board, us, them, king_sq, check_mask, ml)
    _gen_pawn_moves(board, us, them, pinned, king_sq, check_mask, ml)
    _gen_knight_moves(board, us, them, pinned, check_mask, ml)
    _gen_bishop_moves(board, us, them, pinned, king_sq, check_mask, ml)
    _gen_rook_moves(board, us, them, pinned, king_sq, check_mask, ml)
    _gen_queen_moves(board, us, them, pinned, king_sq, check_mask, ml)
    return (ml, checkers, in_check)
def generate_captures(board):
    us = board.turn
    them = us ^ 1
    ml = []
    king_bb = board.pieces[us][K]
    if not king_bb:
        return ml
    king_sq = king_bb.bit_length() - 1
    checkers, pinned = get_attack_info(board, us, king_sq)
    if not checkers:
        check_mask = _FULL
    elif checkers & checkers - 1:
        _gen_king_captures(board, us, them, king_sq, ml)
        return ml
    else:
        checker_sq = checkers.bit_length() - 1
        check_mask = checkers | _BET[king_sq][checker_sq]
    cap_mask = check_mask & board.occ[them]
    _gen_king_captures(board, us, them, king_sq, ml)
    _gen_pawn_captures(board, us, them, pinned, king_sq, check_mask, ml)
    _gen_knight_moves(board, us, them, pinned, cap_mask, ml)
    _gen_bishop_moves(board, us, them, pinned, king_sq, cap_mask, ml)
    _gen_rook_moves(board, us, them, pinned, king_sq, cap_mask, ml)
    _gen_queen_moves(board, us, them, pinned, king_sq, cap_mask, ml)
    return ml
def generate_captures_from_info(board, checkers, pinned):
    us = board.turn
    them = us ^ 1
    ml = []
    king_bb = board.pieces[us][K]
    if not king_bb:
        return ml
    king_sq = king_bb.bit_length() - 1
    if not checkers:
        check_mask = _FULL
    elif checkers & checkers - 1:
        _gen_king_captures(board, us, them, king_sq, ml)
        return ml
    else:
        checker_sq = checkers.bit_length() - 1
        check_mask = checkers | _BET[king_sq][checker_sq]
    cap_mask = check_mask & board.occ[them]
    _gen_king_captures(board, us, them, king_sq, ml)
    _gen_pawn_captures(board, us, them, pinned, king_sq, check_mask, ml)
    _gen_knight_moves(board, us, them, pinned, cap_mask, ml)
    _gen_bishop_moves(board, us, them, pinned, king_sq, cap_mask, ml)
    _gen_rook_moves(board, us, them, pinned, king_sq, cap_mask, ml)
    _gen_queen_moves(board, us, them, pinned, king_sq, cap_mask, ml)
    return ml
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
            self.ep_sq = (fr + to) >> 1
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
_RAY_N_IDX = 0
_RAY_NE_IDX = 1
_RAY_E_IDX = 2
_RAY_SE_IDX = 3
_RAY_S_IDX = 4
_RAY_SW_IDX = 5
_RAY_W_IDX = 6
_RAY_NW_IDX = 7
_MASK16 = 65535
_SIGN16 = 32768
def _S(mg: int, eg: int) -> int:
    return (mg & _MASK16) << 16 | eg & _MASK16
def _mg(s: int) -> int:
    raw = s >> 16 & _MASK16
    return raw - _MASK16 - 1 if raw & _SIGN16 else raw
def _eg(s: int) -> int:
    raw = s & _MASK16
    return raw - _MASK16 - 1 if raw & _SIGN16 else raw
MAT_MG = (82, 337, 365, 477, 1025, 0)
MAT_EG = (94, 281, 297, 512, 936, 0)
PHASE_WEIGHT = (0, 1, 1, 2, 4, 0)
PHASE_MAX = 24
_LAZY_THRESHOLD = 1400
def _make_psqt():
    pawn_mg = [0, 0, 0, 0, 0, 0, 0, 0, 98, 134, 61, 95, 68, 126, 34, -11, -6, 7, 26, 31, 65, 56, 25, -20, -14, 13, 6, 21, 23, 12, 17, -23, -27, -2, -5, 12, 17, 6, 10, -25, -26, -4, -4, -10, 3, 3, 33, -12, -35, -1, -20, -23, -15, 24, 38, -22, 0, 0, 0, 0, 0, 0, 0, 0]
    pawn_eg = [0, 0, 0, 0, 0, 0, 0, 0, 178, 173, 158, 134, 147, 132, 165, 187, 94, 100, 85, 67, 56, 53, 82, 84, 32, 24, 13, 5, -2, 4, 17, 17, 13, 9, -3, -7, -7, -8, 3, -1, 4, 7, -6, 1, 0, -5, -1, -8, 13, 8, 8, 10, 13, 0, 2, -7, 0, 0, 0, 0, 0, 0, 0, 0]
    knight_mg = [-167, -89, -34, -49, 61, -97, -15, -107, -73, -41, 72, 36, 23, 62, 7, -17, -47, 60, 37, 65, 84, 129, 73, 44, -9, 17, 19, 53, 37, 69, 18, 22, -13, 4, 16, 13, 28, 19, 21, -8, -23, -9, 12, 10, 19, 17, 25, -16, -29, -53, -12, -3, -1, 18, -14, -19, -105, -21, -58, -33, -17, -28, -19, -23]
    knight_eg = [-58, -38, -13, -28, -31, -27, -63, -99, -25, -8, -25, -2, -9, -25, -24, -52, -24, -20, 10, 9, -1, -9, -19, -41, -17, 3, 22, 22, 22, 11, 8, -18, -18, -6, 16, 25, 16, 17, 4, -18, -23, -3, -1, 15, 10, -3, -20, -22, -42, -20, -10, -5, -2, -20, -23, -44, -29, -51, -23, -15, -22, -18, -50, -64]
    bishop_mg = [-29, 4, -82, -37, -25, -42, 7, -8, -26, 16, -18, -13, 30, 59, 18, -47, -16, 37, 43, 40, 35, 50, 37, -2, -4, 5, 19, 50, 37, 37, 7, -2, -6, 13, 13, 26, 34, 12, 10, 4, 0, 15, 15, 15, 14, 27, 18, 10, 4, 15, 16, 0, 7, 21, 33, 1, -33, -3, -14, -21, -13, -12, -39, -21]
    bishop_eg = [-14, -21, -11, -8, -7, -9, -17, -24, -8, -4, 7, -12, -3, -13, -4, -14, 2, -8, 0, -1, -2, 6, 0, 4, -3, 9, 12, 9, 14, 10, 3, 2, -6, 3, 13, 19, 7, 10, -3, -9, -12, -3, 8, 10, 13, 3, -7, -15, -14, -18, -7, -1, 4, -9, -15, -27, -23, -9, -23, -5, -9, -16, -5, -17]
    rook_mg = [32, 42, 32, 51, 63, 9, 31, 43, 27, 32, 58, 62, 80, 67, 26, 44, -5, 19, 26, 36, 17, 45, 61, 16, -24, -11, 7, 26, 24, 35, -8, -20, -36, -26, -12, -1, 9, -7, 6, -23, -45, -25, -16, -17, 3, 0, -5, -33, -44, -16, -20, -9, -1, 11, -6, -71, -19, -13, 1, 17, 16, 7, -37, -26]
    rook_eg = [13, 10, 18, 15, 12, 12, 8, 5, 11, 13, 13, 11, -3, 3, 8, 3, 7, 7, 7, 5, 4, -3, -5, -3, 4, 3, 13, 1, 2, 1, -1, 2, 3, 5, 8, 4, -5, -6, -8, -11, -4, 0, -5, -1, -7, -12, -8, -16, -6, -6, 0, 2, -9, -9, -11, -3, -9, 2, 3, -1, -5, -13, 4, -20]
    queen_mg = [-28, 0, 29, 12, 59, 44, 43, 45, -24, -39, -5, 1, -16, 57, 28, 54, -13, -17, 7, 8, 29, 56, 47, 57, -27, -27, -16, -16, -1, 17, -2, 1, -9, -26, -9, -10, -2, -4, 3, -3, -14, 2, -11, -2, -5, 2, 14, 5, -35, -8, 11, 2, 8, 15, -3, 1, -1, -18, -9, 10, -15, -25, -31, -50]
    queen_eg = [-9, 22, 22, 27, 27, 19, 10, 20, -17, 20, 32, 41, 58, 25, 30, 0, -20, 6, 9, 49, 47, 35, 19, 9, 3, 22, 24, 45, 57, 40, 57, 36, -18, 28, 19, 47, 31, 34, 39, 23, -16, -27, 15, 6, 9, 17, 10, 5, -22, -23, -30, -16, -16, -23, -36, -32, -33, -28, -22, -43, -5, -32, -20, -41]
    king_mg = [-65, 23, 16, -15, -56, -34, 2, 13, 29, -1, -20, -7, -8, -4, -38, -29, -9, 24, 2, -16, -20, 6, 22, -22, -17, -20, -12, -27, -30, -25, -14, -36, -49, -1, -27, -39, -46, -44, -33, -51, -14, -14, -22, -46, -44, -30, -15, -27, 1, 7, -8, -64, -43, -16, 9, 8, -15, 36, 12, -54, 8, -28, 24, 14]
    king_eg = [-74, -35, -18, -18, -11, 15, 4, -17, -12, 17, 14, 17, 17, 19, 21, -9, 10, 17, 23, 15, 20, 45, 44, 13, -8, 22, 24, 27, 26, 33, 26, 3, -18, -4, 21, 24, 27, 23, 9, -11, -19, -3, 11, 21, 23, 16, 7, -9, -27, -11, 4, 13, 14, 4, -5, -17, -53, -34, -21, -11, -28, -14, -24, -43]
    tables_raw = [pawn_mg, knight_mg, bishop_mg, rook_mg, queen_mg, king_mg]
    tables_eg = [pawn_eg, knight_eg, bishop_eg, rook_eg, queen_eg, king_eg]
    psqt = []
    for mg_arr, eg_arr in zip(tables_raw, tables_eg):
        packed = [_S(mg_arr[i], eg_arr[i]) for i in range(64)]
        psqt.append(packed)
    return (psqt, [pawn_mg, knight_mg, bishop_mg, rook_mg, queen_mg, king_mg], [pawn_eg, knight_eg, bishop_eg, rook_eg, queen_eg, king_eg])
PSQT, _RAW_MG_TABLES, _RAW_EG_TABLES = _make_psqt()
_MB_RAW = [[(-62, -81), (-53, -56), (-12, -30), (-4, -14), (3, 8), (13, 15), (22, 23), (28, 27), (33, 33)], [(-48, -59), (-20, -23), (16, -3), (26, 13), (38, 24), (51, 42), (55, 54), (63, 57), (63, 65), (68, 73), (81, 78), (81, 86), (91, 88), (98, 97)], [(-58, -76), (-27, -18), (-15, 28), (-10, 55), (-5, 69), (-2, 82), (9, 112), (16, 118), (30, 132), (29, 142), (32, 155), (38, 165), (46, 166), (48, 169), (58, 171)], [(-39, -36), (-21, -15), (3, 8), (3, 18), (14, 34), (22, 54), (28, 61), (41, 73), (43, 79), (48, 92), (56, 94), (60, 104), (60, 113), (66, 120), (67, 123), (70, 126), (71, 133), (73, 136), (79, 140), (88, 143), (88, 148), (99, 166), (102, 170), (102, 175), (106, 184), (109, 191), (113, 206), (116, 212)]]
MOBILITY_BONUS = tuple((tuple((_S(mg, eg) for mg, eg in arr)) for arr in _MB_RAW))
_MOB_MAX = (8, 13, 14, 27)
PASSED_RANK = (_S(0, 0), _S(10, 28), _S(17, 33), _S(15, 41), _S(62, 72), _S(168, 177), _S(276, 260), _S(0, 0))
_BISHOP_PAWNS = _S(3, 7)
_BISHOP_PAIR = _S(37, 65)
_LONG_DIAGONAL_BISHOP = _S(45, 0)
_MINOR_BEHIND_PAWN = _S(18, 3)
_OUTPOST = _S(30, 21)
_REACHABLE_OUTPOST = _S(32, 10)
_KING_PROTECTOR = _S(7, 8)
_ROOK_ON_OPEN_FILE = _S(47, 25)
_ROOK_ON_SEMI_FILE = _S(21, 4)
_ROOK_ON_QUEEN_FILE = _S(7, 6)
_TRAPPED_ROOK = _S(52, 10)
_WEAK_QUEEN = _S(49, 15)
_PASSED_FILE_PENALTY = _S(11, 8)
_ISOLATED_PAWN = _S(15, 9)
_DOUBLED_PAWN = _S(11, 8)
_ISOLATED_DOUBLED = _S(25, 18)
_PAWN_CHAIN = _S(6, 4)
_BACKWARD_PAWN = _S(17, 10)
_PHALANX = _S(12, 7)
_CANDIDATE_PASSED = _S(18, 24)
_ROOK_ON_SEVENTH = _S(23, 11)
_ROOK_BATTERY = _S(12, 6)
_QUEEN_ROOK_BATTERY = _S(8, 4)
_BAD_BISHOP_BLOCKED = _S(5, 0)
_KNIGHT_OUTPOST_PERM = _S(16, 8)
_CENTER_CONTROL_MINOR = _S(4, 2)
_MOPUP_RANK = _S(0, 5)
_MOPUP_DIST = _S(0, 4)
_ENEMY_KING_EDGE_PST = [90, 80, 70, 60, 60, 70, 80, 90, 80, 60, 50, 40, 40, 50, 60, 80, 70, 50, 30, 20, 20, 30, 50, 70, 60, 40, 20, 10, 10, 20, 40, 60, 60, 40, 20, 10, 10, 20, 40, 60, 70, 50, 30, 20, 20, 30, 50, 70, 80, 60, 50, 40, 40, 50, 60, 80, 90, 80, 70, 60, 60, 70, 80, 90]
_ENEMY_KING_CORNER_PST = [100, 85, 70, 55, 55, 70, 85, 100, 85, 60, 45, 30, 30, 45, 60, 85, 70, 45, 25, 12, 12, 25, 45, 70, 55, 30, 12, 0, 0, 12, 30, 55, 55, 30, 12, 0, 0, 12, 30, 55, 70, 45, 25, 12, 12, 25, 45, 70, 85, 60, 45, 30, 30, 45, 60, 85, 100, 85, 70, 55, 55, 70, 85, 100]
_MOPUP_PROXIMITY_BONUS = 30
_MOPUP_EDGE_SCALE = 4
_MOPUP_CORNER_SCALE = 5
_MOPUP_PROXIMITY_SCALE = 10
_XRAY_ATTACK = _S(4, 2)
_SAFE_CHECK = _S(20, 8)
_PAWN_STORM = _S(9, 0)
_KING_SHELTER = _S(14, 0)
_HANGING = _S(30, 18)
_THREAT_BY_KING = _S(16, 50)
_THREAT_BY_PAWN_PUSH = _S(20, 16)
_THREAT_BY_SAFE_PAWN = _S(55, 35)
_PAWNLESS_FLANK = _S(17, 95)
_FLANK_ATTACKS = _S(8, 0)
_TEMPO = 28
_THREAT_BY_MINOR = (_S(0, 0), _S(5, 20), _S(35, 25), _S(45, 32), _S(55, 65), _S(45, 90))
_THREAT_BY_ROOK = (_S(0, 0), _S(2, 28), _S(22, 42), _S(22, 38), _S(0, 24), _S(28, 22))
_KING_ATK_WEIGHT = (0, 0, 81, 52, 44, 10)
_QUEEN_SAFE_CHECK = 780
_ROOK_SAFE_CHECK = 1080
_BISHOP_SAFE_CHECK = 635
_KNIGHT_SAFE_CHECK = 790
_SPACE_THRESHOLD = 5000
FILE_BB = tuple((sum((1 << r * 8 + f for r in range(8))) for f in range(8)))
_QUEENSIDE_MAP = (0, 1, 2, 3, 3, 2, 1, 0)
RANK_BB = (RANK_1, RANK_2, RANK_3, RANK_4, RANK_5, RANK_6, RANK_7, RANK_8)
_OUTPOST_RANKS = (RANK_4 | RANK_5 | RANK_6, RANK_5 | RANK_4 | RANK_3)
_LOW_RANKS = (RANK_2 | RANK_3, RANK_7 | RANK_6)
CENTER_FILES = FILE_BB[2] | FILE_BB[3] | FILE_BB[4] | FILE_BB[5]
QUEEN_SIDE = FILE_BB[0] | FILE_BB[1] | FILE_BB[2] | FILE_BB[3]
KING_SIDE = FILE_BB[4] | FILE_BB[5] | FILE_BB[6] | FILE_BB[7]
CENTER_4SQ = 1 << 27 | 1 << 28 | 1 << 35 | 1 << 36
_SPACE_MASK_W = CENTER_FILES & (RANK_2 | RANK_3 | RANK_4)
_SPACE_MASK_B = CENTER_FILES & (RANK_7 | RANK_6 | RANK_5)
def _build_king_flanks():
    flanks = []
    for f in range(8):
        lo = max(0, f - 1)
        hi = min(7, f + 1)
        bb = 0
        for ff in range(lo, hi + 1):
            bb |= FILE_BB[ff]
        flanks.append(bb)
    return tuple(flanks)
KING_FLANK = _build_king_flanks()
def _build_dist():
    d = [[0] * 64 for _ in range(64)]
    for a in range(64):
        for b in range(64):
            d[a][b] = max(abs(a // 8 - b // 8), abs(a % 8 - b % 8))
    return d
_DIST = _build_dist()
_DARK_SQ = sum((1 << r * 8 + f for r in range(8) for f in range(8) if (r + f) % 2 == 1))
_LIGHT_SQ = FULL_BOARD ^ _DARK_SQ
_BB_SQ = BB_SQUARES
_KA = KNIGHT_ATTACKS
_KING_A = KING_ATTACKS
_PA = PAWN_ATTACKS
_RAY_N = RAYS[_RAY_N_IDX]
_RAY_NE = RAYS[_RAY_NE_IDX]
_RAY_E = RAYS[_RAY_E_IDX]
_RAY_SE = RAYS[_RAY_SE_IDX]
_RAY_S = RAYS[_RAY_S_IDX]
_RAY_SW = RAYS[_RAY_SW_IDX]
_RAY_W = RAYS[_RAY_W_IDX]
_RAY_NW = RAYS[_RAY_NW_IDX]
def _rook_atk(sq: int, occ: int) -> int:
    r = _BB_SQ[sq]
    a = 0
    ray = _RAY_N[sq]
    o = occ & ray
    a |= (o - r - r ^ o) & ray
    ray = _RAY_E[sq]
    o = occ & ray
    a |= (o - r - r ^ o) & ray
    ray = _RAY_S[sq]
    o = occ & ray
    if o:
        msb = 1 << o.bit_length() - 1
        a |= ray ^ ray & msb - 1
    else:
        a |= ray
    ray = _RAY_W[sq]
    o = occ & ray
    if o:
        msb = 1 << o.bit_length() - 1
        a |= ray ^ ray & msb - 1
    else:
        a |= ray
    return a
def _bish_atk(sq: int, occ: int) -> int:
    r = _BB_SQ[sq]
    a = 0
    ray = _RAY_NE[sq]
    o = occ & ray
    a |= (o - r - r ^ o) & ray
    ray = _RAY_NW[sq]
    o = occ & ray
    a |= (o - r - r ^ o) & ray
    ray = _RAY_SE[sq]
    o = occ & ray
    if o:
        msb = 1 << o.bit_length() - 1
        a |= ray ^ ray & msb - 1
    else:
        a |= ray
    ray = _RAY_SW[sq]
    o = occ & ray
    if o:
        msb = 1 << o.bit_length() - 1
        a |= ray ^ ray & msb - 1
    else:
        a |= ray
    return a
def _queen_atk(sq: int, occ: int) -> int:
    return _rook_atk(sq, occ) | _bish_atk(sq, occ)
_popcount = int.bit_count
_NFA = NOT_FILE_A
_NFH = NOT_FILE_H
def _pawn_attacks_white(pawns: int) -> int:
    return ((pawns & _NFH) << 9 | (pawns & _NFA) << 7) & FULL_BOARD
def _pawn_attacks_black(pawns: int) -> int:
    return (pawns & _NFA) >> 7 | (pawns & _NFH) >> 9
def _passed_pawns_white(wpawns: int, bpawns: int) -> int:
    bp = bpawns
    bp |= (bp & _NFA) >> 7 | (bp & _NFH) >> 9
    span = bp | bp >> 8 | bp >> 16 | bp >> 24 | bp >> 32 | bp >> 40 | bp >> 48
    return wpawns & ~span
def _passed_pawns_black(bpawns: int, wpawns: int) -> int:
    wp = wpawns
    wp |= (wp & _NFH) << 9 | (wp & _NFA) << 7
    span = wp | wp << 8 | wp << 16 | wp << 24 | wp << 32 | wp << 40 | wp << 48
    return bpawns & ~(span & FULL_BOARD)
def _king_ring(ksq: int) -> int:
    f = max(1, min(6, ksq % 8))
    r = max(1, min(6, ksq // 8))
    clamped = r * 8 + f
    return _KING_A[clamped] | _BB_SQ[clamped]
def _lsb(bb: int) -> int:
    return (bb & -bb).bit_length() - 1
_NPM_WEIGHT = (0, 337, 365, 477, 1025, 0)
def _non_pawn_material(board) -> int:
    total = 0
    for c in (WHITE, BLACK):
        for pc in (N, B, R, Q):
            total += _NPM_WEIGHT[pc] * _popcount(board.pieces[c][pc])
    return total
def _has_mating_material(board, side: int) -> bool:
    opp = side ^ 1
    if board.pieces[opp][P] or board.pieces[opp][N] or board.pieces[opp][B] or board.pieces[opp][R] or board.pieces[opp][Q]:
        return False
    queens = board.pieces[side][Q]
    rooks = board.pieces[side][R]
    bishops = board.pieces[side][B]
    knights = board.pieces[side][N]
    if queens or rooks:
        return True
    if _popcount(bishops) >= 2:
        return True
    if bishops and knights:
        return True
    return False
def _is_kbnk(board):
    for side in (WHITE, BLACK):
        opp = side ^ 1
        if board.pieces[side][P] | board.pieces[side][R] | board.pieces[side][Q] | board.pieces[opp][P] | board.pieces[opp][R] | board.pieces[opp][Q] | board.pieces[opp][N] | board.pieces[opp][B]:
            continue
        if board.pieces[side][N].bit_count() == 1 and board.pieces[side][B].bit_count() == 1 and (board.pieces[side][Q] == 0) and (board.pieces[opp][N] == 0) and (board.pieces[opp][B] == 0):
            return (side, opp)
    return None
def _is_knnkp(board):
    for side in (WHITE, BLACK):
        opp = side ^ 1
        if board.pieces[side][P] | board.pieces[side][R] | board.pieces[side][Q] | board.pieces[side][B] | board.pieces[opp][R] | board.pieces[opp][Q] | board.pieces[opp][N] | board.pieces[opp][B]:
            continue
        if board.pieces[side][N].bit_count() == 2 and board.pieces[side][Q] == 0 and (board.pieces[opp][N] == 0) and (board.pieces[opp][P].bit_count() == 1):
            pawn_bb = board.pieces[opp][P]
            pawn_sq = (pawn_bb & -pawn_bb).bit_length() - 1
            return (side, opp, pawn_sq)
    return None
_TROITZKY_WHITE = {0: 3, 1: 5, 2: 4, 3: 3, 4: 3, 5: 4, 6: 5, 7: 3}
_TROITZKY_BLACK = {0: 4, 1: 2, 2: 3, 3: 4, 4: 4, 5: 3, 6: 2, 7: 4}
def _troitzky_win_possible(defender_color: int, pawn_sq: int) -> bool:
    file = pawn_sq % 8
    if defender_color == WHITE:
        return pawn_sq // 8 <= _TROITZKY_WHITE[file]
    else:
        return pawn_sq // 8 >= _TROITZKY_BLACK[file]
def _eval_kbnk(board, winner: int, loser: int) -> int:
    bishop_bb = board.pieces[winner][B]
    bishop_is_dark = bool(bishop_bb & _DARK_SQ)
    ek_sq = board.pieces[loser][K].bit_length() - 1
    ok_sq = board.pieces[winner][K].bit_length() - 1
    if bishop_is_dark:
        correct_corners = 1 << 56 | 1 << 7
    else:
        correct_corners = 1 << 0 | 1 << 63
    def cheb(a, b):
        return max(abs(a // 8 - b // 8), abs(a % 8 - b % 8))
    best_dist = 7
    tmp = correct_corners
    while tmp:
        lsb = tmp & -tmp
        corner = lsb.bit_length() - 1
        d = cheb(ek_sq, corner)
        if d < best_dist:
            best_dist = d
        tmp ^= lsb
    score = 800 - 40 * best_dist
    dist_kings = cheb(ok_sq, ek_sq)
    score += (7 - dist_kings) * 10
    knight_bb = board.pieces[winner][N]
    knight_sq = knight_bb.bit_length() - 1
    kn_dist = cheb(knight_sq, ek_sq)
    score += (5 - kn_dist) * 5
    wrong_corners = 1 << 56 | 1 << 7 if not bishop_is_dark else 1 << 0 | 1 << 63
    if 1 << ek_sq & wrong_corners:
        score -= 200
    if best_dist == 0 and dist_kings <= 2:
        score += 2000
    return score
def _eval_knnkp(board, attacker: int, defender: int, pawn_sq: int) -> int:
    if not _troitzky_win_possible(defender, pawn_sq):
        return 0
    ek_sq = board.pieces[defender][K].bit_length() - 1
    ok_sq = board.pieces[attacker][K].bit_length() - 1
    if defender == WHITE:
        block_sq = pawn_sq + 8
    else:
        block_sq = pawn_sq - 8
    knight_bb = board.pieces[attacker][N]
    block_score = 0
    if knight_bb & 1 << block_sq:
        block_score = 500
    king_pawn_dist = max(abs(ok_sq // 8 - pawn_sq // 8), abs(ok_sq % 8 - pawn_sq % 8))
    capture_risk = -300 if king_pawn_dist <= 1 and knight_bb & 1 << block_sq == 0 else 0
    edge_rank = ek_sq // 8 == 0 or ek_sq // 8 == 7
    edge_file = ek_sq % 8 == 0 or ek_sq % 8 == 7
    edge_bonus = 50 if edge_rank else 0
    edge_bonus += 50 if edge_file else 0
    corner_bonus = 200 if edge_rank and edge_file else 0
    king_dist = max(abs(ok_sq // 8 - ek_sq // 8), abs(ok_sq % 8 - ek_sq % 8))
    king_prox = (7 - king_dist) * 10
    score = block_score + capture_risk + edge_bonus + corner_bonus + king_prox + 300
    if defender == WHITE:
        pawn_rank = pawn_sq // 8
        if pawn_rank > 4:
            score -= 20 * (pawn_rank - 4)
    else:
        pawn_rank = 7 - pawn_sq // 8
        if pawn_rank > 4:
            score -= 20 * (pawn_rank - 4)
    return score
def evaluate(board) -> int:
    pW = board.pieces[WHITE]
    pB = board.pieces[BLACK]
    occ = board.all_occ
    turn = board.turn
    phase = 0
    for pc in (N, B, R, Q):
        phase += PHASE_WEIGHT[pc] * (_popcount(pW[pc]) + _popcount(pB[pc]))
    phase = min(phase, PHASE_MAX)
    skip_psqt_white = _has_mating_material(board, WHITE)
    skip_psqt_black = _has_mating_material(board, BLACK)
    score_mg = 0
    score_eg = 0
    _ZERO_PSQ = [0] * 64
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        skip = skip_psqt_white if c == WHITE else skip_psqt_black
        pp = board.pieces[c]
        for pc in range(6):
            bb = pp[pc]
            mat_mg = MAT_MG[pc]
            mat_eg = MAT_EG[pc]
            psqt_tbl = _ZERO_PSQ if skip else PSQT[pc]
            while bb:
                sq = _lsb(bb)
                bb &= bb - 1
                psq = sq if c == WHITE else sq ^ 56
                score_mg += sign * (mat_mg + _mg(psqt_tbl[psq]))
                score_eg += sign * (mat_eg + _eg(psqt_tbl[psq]))
    if _popcount(pW[B]) >= 2:
        score_mg += _mg(_BISHOP_PAIR)
        score_eg += _eg(_BISHOP_PAIR)
    if _popcount(pB[B]) >= 2:
        score_mg -= _mg(_BISHOP_PAIR)
        score_eg -= _eg(_BISHOP_PAIR)
    lazy_score = (score_mg * phase + score_eg * (PHASE_MAX - phase)) // PHASE_MAX
    if lazy_score > _LAZY_THRESHOLD or lazy_score < -_LAZY_THRESHOLD:
        result = lazy_score + _TEMPO
        return result if turn == WHITE else -result
    wp = pW[P]
    bp = pB[P]
    w_pawn_atk = _pawn_attacks_white(wp)
    b_pawn_atk = _pawn_attacks_black(bp)
    w_passed = _passed_pawns_white(wp, bp)
    b_passed = _passed_pawns_black(bp, wp)
    def _w_atk_span(pawns: int) -> int:
        p = pawns
        for _ in range(6):
            p |= ((p & _NFH) << 9 | (p & _NFA) << 7) & FULL_BOARD
        return p
    def _b_atk_span(pawns: int) -> int:
        p = pawns
        for _ in range(6):
            p |= (p & _NFA) >> 7 | (p & _NFH) >> 9
        return p
    w_pawn_span = _w_atk_span(wp)
    b_pawn_span = _b_atk_span(bp)
    ALL = 6
    atk = [[0] * 7, [0] * 7]
    atk2 = [0, 0]
    wksq = _lsb(pW[K])
    bksq = _lsb(pB[K])
    atk[WHITE][K] = _KING_A[wksq]
    atk[BLACK][K] = _KING_A[bksq]
    atk[WHITE][P] = w_pawn_atk
    atk[BLACK][P] = b_pawn_atk
    for c in (WHITE, BLACK):
        atk[c][ALL] = atk[c][K] | atk[c][P]
        ka_x_pa = atk[c][K] & atk[c][P]
        if c == WHITE:
            pp2 = wp & wp - 1
            dbl_pawn = _pawn_attacks_white(pp2) if pp2 else 0
        else:
            pp2 = bp & bp - 1
            dbl_pawn = _pawn_attacks_black(pp2) if pp2 else 0
        atk2[c] = ka_x_pa | dbl_pawn
    w_king_ring = _king_ring(wksq)
    b_king_ring = _king_ring(bksq)
    w_dbl_pawn = _pawn_attacks_white(wp & wp - 1) if wp & wp - 1 else 0
    b_dbl_pawn = _pawn_attacks_black(bp & bp - 1) if bp & bp - 1 else 0
    w_king_ring &= ~w_dbl_pawn
    b_king_ring &= ~b_dbl_pawn
    ka_count = [0, 0]
    ka_weight = [0, 0]
    ka_atk = [0, 0]
    def _mob_area(us: int, them: int) -> int:
        pp_us = board.pieces[us]
        own_pawns = pp_us[P]
        if us == WHITE:
            low_r = _LOW_RANKS[WHITE]
            blocked = own_pawns & (occ >> 8 | low_r)
        else:
            low_r = _LOW_RANKS[BLACK]
            blocked = own_pawns & (occ << 8 & FULL_BOARD | low_r)
        excluded = blocked | pp_us[K] | pp_us[Q]
        enemy_pawn_atk = b_pawn_atk if us == WHITE else w_pawn_atk
        return ~(excluded | enemy_pawn_atk) & FULL_BOARD
    mob_area_w = _mob_area(WHITE, BLACK)
    mob_area_b = _mob_area(BLACK, WHITE)
    mob_area = [mob_area_w, mob_area_b]
    mob_score_mg = [0, 0]
    mob_score_eg = [0, 0]
    piece_score_mg = 0
    piece_score_eg = 0
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        them = c ^ 1
        pp = board.pieces[c]
        occ_them = board.occ[them]
        ksq_us = wksq if c == WHITE else bksq
        their_king_ring = b_king_ring if c == WHITE else w_king_ring
        m_area = mob_area[c]
        outpost_ranks = _OUTPOST_RANKS[c]
        own_pawn_atk = w_pawn_atk if c == WHITE else b_pawn_atk
        enemy_pawn_span = b_pawn_span if c == WHITE else w_pawn_span
        bb = pp[N]
        atk[c][N] = 0
        while bb:
            sq = _lsb(bb)
            bb &= bb - 1
            a = _KA[sq]
            atk[c][N] |= a
            atk2[c] |= atk[c][ALL] & a
            atk[c][ALL] |= a
            if a & their_king_ring:
                ka_count[c] += 1
                ka_weight[c] += _KING_ATK_WEIGHT[N]
                ka_atk[c] += _popcount(a & _KING_A[bksq if c == WHITE else wksq])
            mob = _popcount(a & m_area)
            mob = min(mob, _MOB_MAX[0])
            s = MOBILITY_BONUS[0][mob]
            mob_score_mg[c] += _mg(s)
            mob_score_eg[c] += _eg(s)
            sq_bb = _BB_SQ[sq]
            if sq_bb & outpost_ranks & own_pawn_atk & ~enemy_pawn_span:
                piece_score_mg += sign * _mg(_OUTPOST) * 2
                piece_score_eg += sign * _eg(_OUTPOST) * 2
            elif a & ~board.occ[c] & outpost_ranks & own_pawn_atk & ~enemy_pawn_span:
                piece_score_mg += sign * _mg(_REACHABLE_OUTPOST)
                piece_score_eg += sign * _eg(_REACHABLE_OUTPOST)
            if c == WHITE:
                if sq_bb << 8 & (wp | bp):
                    piece_score_mg += sign * _mg(_MINOR_BEHIND_PAWN)
                    piece_score_eg += sign * _eg(_MINOR_BEHIND_PAWN)
            elif sq_bb >> 8 & (wp | bp):
                piece_score_mg += sign * _mg(_MINOR_BEHIND_PAWN)
                piece_score_eg += sign * _eg(_MINOR_BEHIND_PAWN)
            d = _DIST[sq][ksq_us]
            piece_score_mg -= sign * _mg(_KING_PROTECTOR) * d
            piece_score_eg -= sign * _eg(_KING_PROTECTOR) * d
        bb = pp[B]
        atk[c][B] = 0
        while bb:
            sq = _lsb(bb)
            bb &= bb - 1
            a = _bish_atk(sq, occ ^ pp[Q])
            atk[c][B] |= a
            atk2[c] |= atk[c][ALL] & a
            atk[c][ALL] |= a
            if a & their_king_ring:
                ka_count[c] += 1
                ka_weight[c] += _KING_ATK_WEIGHT[B]
                ka_atk[c] += _popcount(a & _KING_A[bksq if c == WHITE else wksq])
            mob = _popcount(a & m_area)
            mob = min(mob, _MOB_MAX[1])
            s = MOBILITY_BONUS[1][mob]
            mob_score_mg[c] += _mg(s)
            mob_score_eg[c] += _eg(s)
            sq_bb = _BB_SQ[sq]
            if sq_bb & outpost_ranks & own_pawn_atk & ~enemy_pawn_span:
                piece_score_mg += sign * _mg(_OUTPOST)
                piece_score_eg += sign * _eg(_OUTPOST)
            if c == WHITE:
                if sq_bb << 8 & (wp | bp):
                    piece_score_mg += sign * _mg(_MINOR_BEHIND_PAWN)
                    piece_score_eg += sign * _eg(_MINOR_BEHIND_PAWN)
            elif sq_bb >> 8 & (wp | bp):
                piece_score_mg += sign * _mg(_MINOR_BEHIND_PAWN)
                piece_score_eg += sign * _eg(_MINOR_BEHIND_PAWN)
            piece_score_mg -= sign * _mg(_KING_PROTECTOR) * _DIST[sq][ksq_us]
            piece_score_eg -= sign * _eg(_KING_PROTECTOR) * _DIST[sq][ksq_us]
            color_sq = _DARK_SQ if sq_bb & _DARK_SQ else _LIGHT_SQ
            n_same_color_pawns = _popcount(pp[P] & color_sq)
            if c == WHITE:
                blocked_center = _popcount(wp & (occ >> 8 & CENTER_FILES))
            else:
                blocked_center = _popcount(bp & (occ << 8 & FULL_BOARD & CENTER_FILES))
            piece_score_mg -= sign * _mg(_BISHOP_PAWNS) * n_same_color_pawns * (1 + blocked_center)
            piece_score_eg -= sign * _eg(_BISHOP_PAWNS) * n_same_color_pawns * (1 + blocked_center)
            center_bb = _BB_SQ[27] | _BB_SQ[28] | _BB_SQ[35] | _BB_SQ[36]
            if _popcount(_bish_atk(sq, wp | bp) & center_bb) >= 2:
                piece_score_mg += sign * _mg(_LONG_DIAGONAL_BISHOP)
                piece_score_eg += sign * _eg(_LONG_DIAGONAL_BISHOP)
        bb = pp[R]
        atk[c][R] = 0
        while bb:
            sq = _lsb(bb)
            bb &= bb - 1
            a = _rook_atk(sq, occ ^ pp[Q] ^ pp[R])
            atk[c][R] |= a
            atk2[c] |= atk[c][ALL] & a
            atk[c][ALL] |= a
            if a & their_king_ring:
                ka_count[c] += 1
                ka_weight[c] += _KING_ATK_WEIGHT[R]
                ka_atk[c] += _popcount(a & _KING_A[bksq if c == WHITE else wksq])
            mob = _popcount(a & m_area)
            mob = min(mob, _MOB_MAX[2])
            s = MOBILITY_BONUS[2][mob]
            mob_score_mg[c] += _mg(s)
            mob_score_eg[c] += _eg(s)
            file_of_sq = sq % 8
            f_bb = FILE_BB[file_of_sq]
            if not pp[P] & f_bb:
                if not board.pieces[them][P] & f_bb:
                    piece_score_mg += sign * _mg(_ROOK_ON_OPEN_FILE)
                    piece_score_eg += sign * _eg(_ROOK_ON_OPEN_FILE)
                else:
                    piece_score_mg += sign * _mg(_ROOK_ON_SEMI_FILE)
                    piece_score_eg += sign * _eg(_ROOK_ON_SEMI_FILE)
            elif mob <= 3:
                kf = ksq_us % 8
                if (kf < 4) == (file_of_sq < kf):
                    can_castle = bool(board.castling & (1 if c == WHITE else 12))
                    mult = 1 if can_castle else 2
                    piece_score_mg -= sign * _mg(_TRAPPED_ROOK) * mult
                    piece_score_eg -= sign * _eg(_TRAPPED_ROOK) * mult
            if f_bb & (pp[Q] | board.pieces[them][Q]):
                piece_score_mg += sign * _mg(_ROOK_ON_QUEEN_FILE)
                piece_score_eg += sign * _eg(_ROOK_ON_QUEEN_FILE)
        bb = pp[Q]
        atk[c][Q] = 0
        while bb:
            sq = _lsb(bb)
            bb &= bb - 1
            a = _queen_atk(sq, occ)
            atk[c][Q] |= a
            atk2[c] |= atk[c][ALL] & a
            atk[c][ALL] |= a
            if a & their_king_ring:
                ka_count[c] += 1
                ka_weight[c] += _KING_ATK_WEIGHT[Q]
                ka_atk[c] += _popcount(a & _KING_A[bksq if c == WHITE else wksq])
            mob = _popcount(a & m_area)
            mob = min(mob, _MOB_MAX[3])
            s = MOBILITY_BONUS[3][mob]
            mob_score_mg[c] += _mg(s)
            mob_score_eg[c] += _eg(s)
    score_mg += mob_score_mg[WHITE] - mob_score_mg[BLACK]
    score_eg += mob_score_eg[WHITE] - mob_score_eg[BLACK]
    score_mg += piece_score_mg
    score_eg += piece_score_eg
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        them = c ^ 1
        ksq = wksq if c == WHITE else bksq
        weak = atk[them][ALL] & ~atk2[c] & (~atk[c][ALL] | atk[c][K] | atk[c][Q])
        safe_sq = ~board.occ[them] & (~atk[c][ALL] | weak & atk2[them])
        b1 = _rook_atk(ksq, occ ^ board.pieces[c][Q])
        b2 = _bish_atk(ksq, occ ^ board.pieces[c][Q])
        king_danger = 0
        rook_checks = b1 & safe_sq & atk[them][R]
        if rook_checks:
            king_danger += _ROOK_SAFE_CHECK
        queen_checks = (b1 | b2) & atk[them][Q] & safe_sq & ~atk[c][Q] & ~rook_checks
        if queen_checks:
            king_danger += _QUEEN_SAFE_CHECK
        bishop_checks = b2 & atk[them][B] & safe_sq & ~queen_checks
        if bishop_checks:
            king_danger += _BISHOP_SAFE_CHECK
        knight_checks = _KA[ksq] & atk[them][N]
        if knight_checks & safe_sq:
            king_danger += _KNIGHT_SAFE_CHECK
        king_ring_here = w_king_ring if c == WHITE else b_king_ring
        weak_in_ring = _popcount(king_ring_here & weak)
        king_danger += ka_count[them] * ka_weight[them] + 185 * weak_in_ring + 69 * ka_atk[them] - 873 * (1 if not board.pieces[them][Q] else 0) - 100 * bool(atk[c][N] & atk[c][K]) - 6 * mob_score_mg[c] // 8 + 37
        if king_danger > 100:
            score_mg -= sign * (king_danger * king_danger // 4096)
            score_eg -= sign * (king_danger // 16)
        kf = ksq % 8
        if not (wp | bp) & KING_FLANK[kf]:
            score_mg -= sign * _mg(_PAWNLESS_FLANK)
            score_eg -= sign * _eg(_PAWNLESS_FLANK)
        camp = FULL_BOARD ^ (RANK_6 | RANK_7 | RANK_8) if c == WHITE else FULL_BOARD ^ (RANK_1 | RANK_2 | RANK_3)
        b1_fa = atk[them][ALL] & KING_FLANK[kf] & camp
        flank_atk = _popcount(b1_fa) + _popcount(b1_fa & atk2[them])
        score_mg -= sign * _mg(_FLANK_ATTACKS) * flank_atk
        score_eg -= sign * _eg(_FLANK_ATTACKS) * flank_atk
        if board.pieces[them][Q]:
            krank = ksq // 8
            kfile = ksq % 8
            if 2 <= kfile <= 5:
                center_rank_dist = krank if c == WHITE else 7 - krank
                score_mg -= sign * 20 * (center_rank_dist + 1)
            back_rank = 0 if c == WHITE else 7
            if krank != back_rank and 2 <= kfile <= 5:
                score_mg -= sign * 50
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        them = c ^ 1
        passed_bb = w_passed if c == WHITE else b_passed
        ksq_us = wksq if c == WHITE else bksq
        ksq_them = bksq if c == WHITE else wksq
        while passed_bb:
            sq = _lsb(passed_bb)
            passed_bb &= passed_bb - 1
            rk = sq // 8 if c == WHITE else 7 - sq // 8
            s = PASSED_RANK[rk]
            bmg = _mg(s)
            beg = _eg(s)
            if rk > 2:
                w = 5 * rk - 13
                block_sq = sq + 8 if c == WHITE else sq - 8
                d_them = min(_DIST[ksq_them][block_sq], 5)
                d_us = min(_DIST[ksq_us][block_sq], 5)
                beg += (d_them * 19 // 4 - d_us * 2) * w
                if rk != 6:
                    next_sq = block_sq + 8 if c == WHITE else block_sq - 8
                    if 0 <= next_sq < 64:
                        d_us2 = min(_DIST[ksq_us][next_sq], 5)
                        beg -= d_us2 * w
                if not occ & _BB_SQ[block_sq]:
                    k = 35
                    fwd = 0
                    tmp = _BB_SQ[block_sq]
                    for _ in range(6):
                        if c == WHITE:
                            tmp = tmp << 8 & FULL_BOARD
                        else:
                            tmp = tmp >> 8
                        fwd |= tmp
                    unsafe = fwd & atk[them][ALL]
                    block_attacked = bool(atk[them][ALL] & _BB_SQ[block_sq])
                    if block_attacked:
                        k = 0
                    elif unsafe:
                        k = 9
                    else:
                        k = 20
                    if atk[c][ALL] & _BB_SQ[block_sq] or board.occ[c] & fwd:
                        k += 5
                    bmg += k * w
                    beg += k * w
            if c == WHITE:
                if sq < 56:
                    bs = sq + 8
                    if occ & _BB_SQ[bs]:
                        bmg //= 2
                        beg //= 2
            elif sq > 7:
                bs = sq - 8
                if occ & _BB_SQ[bs]:
                    bmg //= 2
                    beg //= 2
            f = sq % 8
            bmg -= _mg(_PASSED_FILE_PENALTY) * _QUEENSIDE_MAP[f]
            beg -= _eg(_PASSED_FILE_PENALTY) * _QUEENSIDE_MAP[f]
            score_mg += sign * bmg
            score_eg += sign * beg
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        own_pawns = board.pieces[c][P]
        if not own_pawns:
            continue
        iso_mg = _mg(_ISOLATED_PAWN)
        iso_eg = _eg(_ISOLATED_PAWN)
        dbl_mg = _mg(_DOUBLED_PAWN)
        dbl_eg = _eg(_DOUBLED_PAWN)
        iso_dbl_mg = _mg(_ISOLATED_DOUBLED)
        iso_dbl_eg = _eg(_ISOLATED_DOUBLED)
        chn_mg = _mg(_PAWN_CHAIN)
        chn_eg = _eg(_PAWN_CHAIN)
        for f in range(8):
            pawns_on_file = own_pawns & FILE_BB[f]
            if not pawns_on_file:
                continue
            count = _popcount(pawns_on_file)
            adj = 0
            if f > 0:
                adj |= own_pawns & FILE_BB[f - 1]
            if f < 7:
                adj |= own_pawns & FILE_BB[f + 1]
            is_isolated = not adj
            if is_isolated:
                score_mg -= sign * iso_mg * count
                score_eg -= sign * iso_eg * count
            if count > 1:
                score_mg -= sign * dbl_mg * (count - 1)
                score_eg -= sign * dbl_eg * (count - 1)
                if is_isolated:
                    score_mg -= sign * iso_dbl_mg * (count - 1)
                    score_eg -= sign * iso_dbl_eg * (count - 1)
        if c == WHITE:
            defenders = (own_pawns & _NFH) >> 9 | (own_pawns & _NFA) >> 7
        else:
            defenders = (own_pawns & _NFA) << 7 | (own_pawns & _NFH) << 9
        chain_count = _popcount(own_pawns & defenders & FULL_BOARD)
        score_mg += sign * chn_mg * chain_count
        score_eg += sign * chn_eg * chain_count
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        them = c ^ 1
        occ_them = board.occ[them]
        pp_them = board.pieces[them]
        pp_us = board.pieces[c]
        non_pawn_enemies = occ_them & ~pp_them[P]
        strongly_prot = atk[them][P] | atk2[them] & ~atk2[c]
        defended = non_pawn_enemies & strongly_prot
        weak = occ_them & ~strongly_prot & atk[c][ALL]
        if defended | weak:
            b_minor = (defended | weak) & (atk[c][N] | atk[c][B])
            while b_minor:
                sq = _lsb(b_minor)
                b_minor &= b_minor - 1
                pc_there = board.piece_at[sq]
                if 0 <= pc_there <= 5:
                    s = _THREAT_BY_MINOR[pc_there]
                    score_mg += sign * _mg(s)
                    score_eg += sign * _eg(s)
            b_rook = weak & atk[c][R]
            while b_rook:
                sq = _lsb(b_rook)
                b_rook &= b_rook - 1
                pc_there = board.piece_at[sq]
                if 0 <= pc_there <= 5:
                    s = _THREAT_BY_ROOK[pc_there]
                    score_mg += sign * _mg(s)
                    score_eg += sign * _eg(s)
            if weak & atk[c][K]:
                score_mg += sign * _mg(_THREAT_BY_KING)
                score_eg += sign * _eg(_THREAT_BY_KING)
            unattacked = ~atk[them][ALL] | non_pawn_enemies & atk2[c]
            n_hanging = _popcount(weak & unattacked)
            score_mg += sign * _mg(_HANGING) * n_hanging
            score_eg += sign * _eg(_HANGING) * n_hanging
        safe_us = ~atk[them][ALL] | atk[c][ALL]
        b_safe_pawns = pp_us[P] & safe_us
        if c == WHITE:
            safe_pawn_atk = _pawn_attacks_white(b_safe_pawns)
        else:
            safe_pawn_atk = _pawn_attacks_black(b_safe_pawns)
        n_spt = _popcount(safe_pawn_atk & non_pawn_enemies)
        score_mg += sign * _mg(_THREAT_BY_SAFE_PAWN) * n_spt
        score_eg += sign * _eg(_THREAT_BY_SAFE_PAWN) * n_spt
        if c == WHITE:
            push = pp_us[P] << 8 & ~occ & FULL_BOARD
            push2 = (push & RANK_3) << 8 & ~occ & FULL_BOARD
            push_all = push | push2
            push_atk = _pawn_attacks_white(push_all)
        else:
            push = pp_us[P] >> 8 & ~occ
            push2 = (push & RANK_6) >> 8 & ~occ
            push_all = push | push2
            push_atk = _pawn_attacks_black(push_all)
        push_atk &= ~atk[them][P] & safe_us
        n_pp = _popcount(push_atk & non_pawn_enemies)
        score_mg += sign * _mg(_THREAT_BY_PAWN_PUSH) * n_pp
        score_eg += sign * _eg(_THREAT_BY_PAWN_PUSH) * n_pp
    npm = _non_pawn_material(board)
    if npm >= _SPACE_THRESHOLD:
        for c in (WHITE, BLACK):
            sign = 1 if c == WHITE else -1
            them = c ^ 1
            pp_us = board.pieces[c]
            space_mask = _SPACE_MASK_W if c == WHITE else _SPACE_MASK_B
            enemy_pawn_atk = b_pawn_atk if c == WHITE else w_pawn_atk
            safe = space_mask & ~pp_us[P] & ~enemy_pawn_atk
            behind = pp_us[P]
            if c == WHITE:
                behind |= behind >> 8
                behind |= behind >> 16
            else:
                behind |= behind << 8 & FULL_BOARD
                behind |= behind << 16 & FULL_BOARD
            bonus = _popcount(safe) + _popcount(behind & safe & ~atk[them][ALL])
            weight = min(8, _popcount(board.occ[c]) - 1)
            space_score = bonus * weight * weight // 16
            space_score = min(space_score, 40)
            score_mg += sign * space_score
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        own_pawns = board.pieces[c][P]
        them_pawns = board.pieces[c ^ 1][P]
        if not own_pawns:
            continue
        bp_mg = _mg(_BACKWARD_PAWN)
        bp_eg = _eg(_BACKWARD_PAWN)
        tmp = own_pawns
        while tmp:
            sq = (tmp & -tmp).bit_length() - 1
            tmp &= tmp - 1
            f = sq % 8
            stop = sq + 8 if c == WHITE else sq - 8
            if stop < 0 or stop > 63:
                continue
            behind_mask = (1 << sq) - 1 if c == WHITE else (FULL_BOARD ^ (1 << sq + 1) - 1) & FULL_BOARD
            if own_pawns & FILE_BB[f] & behind_mask:
                continue
            adj_sup = 0
            if f > 0:
                adj_sup |= own_pawns & FILE_BB[f - 1]
            if f < 7:
                adj_sup |= own_pawns & FILE_BB[f + 1]
            if not adj_sup:
                continue
            if not PAWN_ATTACKS[c][stop] & them_pawns:
                continue
            score_mg -= sign * bp_mg
            score_eg -= sign * bp_eg
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        own_pawns = board.pieces[c][P]
        ph_mg = _mg(_PHALANX)
        ph_eg = _eg(_PHALANX)
        shifted = (own_pawns & _NFH) << 1 | (own_pawns & _NFA) >> 1
        ph_count = _popcount(own_pawns & shifted) // 2
        score_mg += sign * ph_mg * ph_count
        score_eg += sign * ph_eg * ph_count
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        own_pawns = board.pieces[c][P]
        them_pawns = board.pieces[c ^ 1][P]
        cp_mg = _mg(_CANDIDATE_PASSED)
        cp_eg = _eg(_CANDIDATE_PASSED)
        if not own_pawns or not them_pawns:
            continue
        for f in range(8):
            if not own_pawns & FILE_BB[f]:
                continue
            own_helpers = _popcount(own_pawns & ((FILE_BB[f - 1] if f > 0 else 0) | (FILE_BB[f + 1] if f < 7 else 0)))
            them_helpers = _popcount(them_pawns & ((FILE_BB[f - 1] if f > 0 else 0) | (FILE_BB[f + 1] if f < 7 else 0)))
            them_on_file = _popcount(them_pawns & FILE_BB[f])
            if them_on_file > 0 and own_helpers > them_helpers:
                score_mg += sign * cp_mg
                score_eg += sign * cp_eg
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        seventh_rank = RANK_7 if c == WHITE else RANK_2
        enemy_back = RANK_8 if c == WHITE else RANK_1
        rooks = board.pieces[c][R]
        on_seventh = rooks & seventh_rank
        if on_seventh:
            n = _popcount(on_seventh)
            score_mg += sign * _mg(_ROOK_ON_SEVENTH) * n
            score_eg += sign * _eg(_ROOK_ON_SEVENTH) * n
            ek_sq = bksq if c == WHITE else wksq
            if 1 << ek_sq & enemy_back:
                score_mg += sign * _mg(_ROOK_ON_SEVENTH) * n
                score_eg += sign * _eg(_ROOK_ON_SEVENTH) * n
        if _popcount(rooks) >= 2:
            bb = rooks
            sqs = []
            while bb:
                sq = (bb & -bb).bit_length() - 1
                sqs.append(sq)
                bb &= bb - 1
            for i in range(len(sqs)):
                for j in range(i + 1, len(sqs)):
                    a, b_sq = (sqs[i], sqs[j])
                    if a % 8 == b_sq % 8 or a // 8 == b_sq // 8:
                        score_mg += sign * _mg(_ROOK_BATTERY)
                        score_eg += sign * _eg(_ROOK_BATTERY)
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        knights = board.pieces[c][N]
        them_pawns = board.pieces[c ^ 1][P]
        outpost_ranks = _OUTPOST_RANKS[c]
        while knights:
            sq = (knights & -knights).bit_length() - 1
            knights &= knights - 1
            if not 1 << sq & outpost_ranks:
                continue
            if PAWN_ATTACKS[c][sq] & them_pawns:
                continue
            f = sq % 8
            adj_files = (FILE_BB[f - 1] if f > 0 else 0) | (FILE_BB[f + 1] if f < 7 else 0)
            enemy_pawn_on_adj = them_pawns & adj_files
            if not enemy_pawn_on_adj:
                score_mg += sign * _mg(_KNIGHT_OUTPOST_PERM)
                score_eg += sign * _eg(_KNIGHT_OUTPOST_PERM)
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        center = CENTER_4SQ
        on_center = _popcount((board.pieces[c][N] | board.pieces[c][B]) & center)
        atk_center = _popcount((atk[c][N] | atk[c][B]) & center)
        score_mg += sign * _mg(_CENTER_CONTROL_MINOR) * (on_center * 2 + atk_center)
        score_eg += sign * _eg(_CENTER_CONTROL_MINOR) * (on_center * 2 + atk_center)
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        ksq = wksq if c == WHITE else bksq
        kf = ksq % 8
        if kf not in (0, 1, 6, 7):
            continue
        flank = KING_FLANK[kf]
        own_pawns = board.pieces[c][P]
        them_pawns = board.pieces[c ^ 1][P]
        sh = _mg(_KING_SHELTER)
        for delta in (8, 16) if c == WHITE else (-8, -16):
            sq2 = ksq + delta
            if 0 <= sq2 < 64 and 1 << sq2 & own_pawns & flank:
                score_mg += sign * sh
        storm_zone = flank & (RANK_5 | RANK_4 | RANK_3) if c == WHITE else flank & (RANK_4 | RANK_5 | RANK_6)
        storm_count = _popcount(them_pawns & storm_zone)
        score_mg -= sign * _mg(_PAWN_STORM) * storm_count
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        them = c ^ 1
        n_q = _popcount(board.pieces[c][Q])
        n_r = _popcount(board.pieces[c][R])
        n_b = _popcount(board.pieces[c][B])
        n_n = _popcount(board.pieces[c][N])
        if not (n_q or n_r or n_b or n_n):
            continue
        own_npm = n_n * 300 + n_b * 300 + n_r * 500 + n_q * 900 + _popcount(board.pieces[c][P]) * 100
        them_npm = _popcount(board.pieces[them][N]) * 300 + _popcount(board.pieces[them][B]) * 300 + _popcount(board.pieces[them][R]) * 500 + _popcount(board.pieces[them][Q]) * 900 + _popcount(board.pieces[them][P]) * 100
        advantage = own_npm - them_npm
        if advantage < 150:
            continue
        scale = min(256, (advantage - 150) * 256 // 250)
        ek_sq = bksq if c == WHITE else wksq
        ok_sq = wksq if c == WHITE else bksq
        k_dist = _DIST[ok_sq][ek_sq]
        only_bishops = n_b >= 2 and (not n_q) and (not n_r)
        if only_bishops:
            pst_bonus = _ENEMY_KING_CORNER_PST[ek_sq] * _MOPUP_CORNER_SCALE
        else:
            pst_bonus = _ENEMY_KING_EDGE_PST[ek_sq] * _MOPUP_EDGE_SCALE
        prox_bonus = _MOPUP_PROXIMITY_BONUS * (14 - k_dist)
        total_mopup = (pst_bonus + prox_bonus) * scale // 256
        score_eg += sign * total_mopup
    _UPP_VAL = (0, 300, 310, 500, 950, 99999)
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        them = c ^ 1
        for pc in (N, B, R, Q):
            bb = board.pieces[c][pc]
            while bb:
                sq = _lsb(bb)
                bb &= bb - 1
                sq_bb = _BB_SQ[sq]
                if not atk[them][ALL] & sq_bb:
                    continue
                cheapest = 99999
                for apc in (P, N, B, R, Q, K):
                    if atk[them][apc] & sq_bb:
                        cheapest = _UPP_VAL[apc]
                        break
                if cheapest < _UPP_VAL[pc]:
                    penalty = (_UPP_VAL[pc] - cheapest) // 3
                    score_mg -= sign * penalty
                    score_eg -= sign * penalty
    if phase < 6:
        for c in (WHITE, BLACK):
            sign = 1 if c == WHITE else -1
            passed_bb = w_passed if c == WHITE else b_passed
            if not passed_bb:
                continue
            them = c ^ 1
            ek_sq = bksq if c == WHITE else wksq
            tmp = passed_bb
            while tmp:
                sq = (tmp & -tmp).bit_length() - 1
                tmp &= tmp - 1
                pawn_rank = sq // 8
                promo_sq = sq % 8 + (56 if c == WHITE else 0)
                pawn_dist = 7 - pawn_rank if c == WHITE else pawn_rank
                king_dist = _DIST[ek_sq][promo_sq]
                if board.turn == c:
                    pawn_dist = max(1, pawn_dist)
                else:
                    pawn_dist = max(1, pawn_dist + 1)
                if king_dist > pawn_dist:
                    score_eg += sign * 200
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        them = c ^ 1
        xr_mg = _mg(_XRAY_ATTACK)
        xr_eg = _eg(_XRAY_ATTACK)
        rooks = board.pieces[c][R]
        while rooks:
            sq = (rooks & -rooks).bit_length() - 1
            rooks &= rooks - 1
            xray_occ = occ ^ board.occ[c]
            xray_atk = _rook_atk(sq, xray_occ)
            extra = xray_atk & board.pieces[them][Q]
            if extra:
                score_mg += sign * xr_mg * _popcount(extra)
                score_eg += sign * xr_eg * _popcount(extra)
        bishops = board.pieces[c][B]
        while bishops:
            sq = (bishops & -bishops).bit_length() - 1
            bishops &= bishops - 1
            xray_occ = occ ^ board.occ[c]
            xray_atk = _bish_atk(sq, xray_occ)
            extra = xray_atk & board.pieces[them][Q]
            if extra:
                score_mg += sign * xr_mg * _popcount(extra)
                score_eg += sign * xr_eg * _popcount(extra)
    outflanking = abs(wksq % 8 - bksq % 8) - abs(wksq // 8 - bksq // 8)
    infiltration = wksq // 8 > 3 or bksq // 8 < 4
    pawns_both_flanks = bool((wp | bp) & QUEEN_SIDE) and bool((wp | bp) & KING_SIDE)
    n_passed = _popcount(w_passed) + _popcount(b_passed)
    n_pawns = _popcount(wp) + _popcount(bp)
    complexity = 9 * n_passed + 11 * n_pawns + 9 * outflanking + 12 * int(infiltration) + 21 * int(pawns_both_flanks) - 100
    u = ((score_mg > 0) - (score_mg < 0)) * max(min(complexity + 50, 0), -abs(score_mg))
    v = ((score_eg > 0) - (score_eg < 0)) * max(complexity, -abs(score_eg))
    score_mg += u
    score_eg += v
    kbnk = _is_kbnk(board)
    if kbnk is not None:
        winner_side, loser_side = kbnk
        raw = _eval_kbnk(board, winner_side, loser_side)
        if winner_side == WHITE:
            result = raw
        else:
            result = -raw
        return result if board.turn == WHITE else -result
    knnkp = _is_knnkp(board)
    if knnkp is not None:
        attacker, defender, pawn_sq = knnkp
        raw = _eval_knnkp(board, attacker, defender, pawn_sq)
        if attacker == WHITE:
            result = raw
        else:
            result = -raw
        return result if board.turn == WHITE else -result
    result = (score_mg * phase + score_eg * (PHASE_MAX - phase)) // PHASE_MAX
    result += _TEMPO * phase // PHASE_MAX
    return result if turn == WHITE else -result
MG_VALUES = list(MAT_MG)
EG_VALUES = list(MAT_EG)
FLIP = [sq ^ 56 for sq in range(64)]
_W_MG = [list(t) for t in _RAW_MG_TABLES]
_B_MG = [list(t) for t in _RAW_MG_TABLES]
MG_TABLES = [_W_MG, _B_MG]
_W_EG = [list(t) for t in _RAW_EG_TABLES]
_B_EG = [list(t) for t in _RAW_EG_TABLES]
EG_TABLES = [_W_EG, _B_EG]
MATE_SCORE = 100000
INF = MATE_SCORE + 1
MAX_DEPTH = 64
TT_SIZE = 1 << 22
TT_MASK = TT_SIZE - 1
NMP_MIN_D = 3
NMP_BASE_R = 3
NMP_MAX_R = 5
LMR_MIN_D = 3
LMR_MIN_M = 2
IIR_MIN_D = 4
ASPIRATION = 50
DELTA_MARGIN = 150
RFP_MAX_D = 7
RFP_MARGIN = 80
FP_DEPTH = 3
FP_MARGIN = (0, 100, 200, 350)
LMP_BASE = 3
LMP_MAX_D = 7
SE_MIN_D = 8
SE_MARGIN = 90
PROBCUT_MIN_D = 5
PROBCUT_BETA = 200
RAZOR_DEPTH = 2
RAZOR_MARGIN = (0, 150, 250)
SEE_PRUNE_D = 8
TT_EXACT = 0
TT_LOWER = 1
TT_UPPER = 2
_SEE_VAL = [100, 300, 300, 500, 900, 20000]
_MV = [100, 300, 300, 500, 900, 0]
_pv = MG_VALUES
WHITE_TABLES = MG_TABLES[WHITE]
KING_MG_PST = WHITE_TABLES[K]
KING_EG_PST = EG_TABLES[WHITE][K]
_CV_MG_W = [[_pv[pc] + WHITE_TABLES[pc][sq] for sq in range(64)] for pc in range(5)]
_CV_MG_W.append([_pv[K] + KING_MG_PST[sq] for sq in range(64)])
_CV_MG_B = [[_pv[pc] + WHITE_TABLES[pc][FLIP[sq]] for sq in range(64)] for pc in range(5)]
_CV_MG_B.append([_pv[K] + KING_MG_PST[FLIP[sq]] for sq in range(64)])
def _full_score(board):
    pcs = board.pieces
    cw = _CV_MG_W
    cb = _CV_MG_B
    w = bl = 0
    for pc in range(6):
        bb = pcs[WHITE][pc]
        tbl = cw[pc]
        while bb:
            w += tbl[(bb & -bb).bit_length() - 1]
            bb &= bb - 1
        bb = pcs[BLACK][pc]
        tbl = cb[pc]
        while bb:
            bl += tbl[(bb & -bb).bit_length() - 1]
            bb &= bb - 1
    return (w, bl)
def _score_delta(board, move):
    us = board.turn
    them = us ^ 1
    fr = move & 63
    to = move >> 6 & 63
    pc = move >> 16 & 7
    mt = move >> 12 & 15
    cw = _CV_MG_W
    cb = _CV_MG_B
    cus = cw if us == WHITE else cb
    cth = cb if us == WHITE else cw
    dw = db = 0
    if mt >= 8:
        cap = move >> 19 & 7
        pp = promo_piece(move)
        dus = -cus[P][fr] + cus[pp][to]
        dth = -cth[cap][to] if mt >= 12 and cap <= 5 else 0
        if us == WHITE:
            dw = dus
            db = dth
        else:
            db = dus
            dw = dth
    elif mt == 5:
        cap_sq = board.ep_sq + (-8 if us == WHITE else 8)
        dus = -cus[P][fr] + cus[P][to]
        dth = -cth[P][cap_sq]
        if us == WHITE:
            dw = dus
            db = dth
        else:
            db = dus
            dw = dth
    elif mt == 2 or mt == 3:
        flag = (CASTLE_WK if us == WHITE else CASTLE_BK) if mt == 2 else CASTLE_WQ if us == WHITE else CASTLE_BQ
        rf = CASTLE_ROOK_FROM[flag]
        rt = CASTLE_ROOK_TO[flag]
        dus = -cus[K][fr] + cus[K][to] - cus[R][rf] + cus[R][rt]
        if us == WHITE:
            dw = dus
        else:
            db = dus
    elif move & FLAG_CAPTURE:
        cap = move >> 19 & 7
        dus = -cus[pc][fr] + cus[pc][to]
        dth = -cth[cap][to] if cap <= 5 else 0
        if us == WHITE:
            dw = dus
            db = dth
        else:
            db = dus
            dw = dth
    else:
        dus = -cus[pc][fr] + cus[pc][to]
        if us == WHITE:
            dw = dus
        else:
            db = dus
    return (dw, db)
_rng = random.Random(3735928559)
_ZP = [[_rng.getrandbits(64) for _ in range(64)] for _ in range(12)]
_ZT = _rng.getrandbits(64)
_ZC = [_rng.getrandbits(64) for _ in range(16)]
_ZE = [_rng.getrandbits(64) for _ in range(65)]
def _full_hash(board) -> int:
    h = 0
    ow = board.occ[WHITE]
    pa = board.piece_at
    zp = _ZP
    for sq in range(64):
        pc = pa[sq]
        if pc != -1:
            h ^= zp[pc + (0 if ow >> sq & 1 else 6)][sq]
    if board.turn == BLACK:
        h ^= _ZT
    h ^= _ZC[board.castling & 15]
    ep = board.ep_sq
    h ^= _ZE[ep if ep != -1 else 64]
    return h
def _delta_hash(board, move: int, old_h: int) -> int:
    us = board.turn
    them = us ^ 1
    fr = move & 63
    to = move >> 6 & 63
    pc = move >> 16 & 7
    mt = move >> 12 & 15
    old_ep = board.ep_sq
    old_cr = board.castling
    zp = _ZP
    h = old_h
    ze = _ZE
    ep64 = old_ep if old_ep != -1 else 64
    zpc_us = pc + (0 if us == WHITE else 6)
    h ^= zp[zpc_us][fr] ^ zp[zpc_us][to]
    if mt == 1:
        h ^= ze[ep64] ^ ze[(fr + to) >> 1]
    elif mt == 5:
        h ^= zp[P + (0 if them == WHITE else 6)][old_ep + (-8 if us == WHITE else 8)]
        h ^= ze[ep64] ^ ze[64]
    elif mt == 2 or mt == 3:
        flag = (CASTLE_WK if us == WHITE else CASTLE_BK) if mt == 2 else CASTLE_WQ if us == WHITE else CASTLE_BQ
        rf = CASTLE_ROOK_FROM[flag]
        rt = CASTLE_ROOK_TO[flag]
        zr = R + (0 if us == WHITE else 6)
        h ^= zp[zr][rf] ^ zp[zr][rt]
        h ^= ze[ep64] ^ ze[64]
    elif mt >= 8:
        cap = move >> 19 & 7
        h ^= zp[zpc_us][to]
        h ^= zp[promo_piece(move) + (0 if us == WHITE else 6)][to]
        if mt >= 12 and cap <= 5:
            h ^= zp[cap + (0 if them == WHITE else 6)][to]
        h ^= ze[ep64] ^ ze[64]
    elif mt == 4:
        cap = move >> 19 & 7
        if cap <= 5:
            h ^= zp[cap + (0 if them == WHITE else 6)][to]
        h ^= ze[ep64] ^ ze[64]
    else:
        h ^= ze[ep64] ^ ze[64]
    new_cr = old_cr & CASTLE_RIGHTS_MASK[fr] & CASTLE_RIGHTS_MASK[to]
    if new_cr != old_cr:
        h ^= _ZC[old_cr & 15] ^ _ZC[new_cr & 15]
    return h ^ _ZT
_TT = [None] * TT_SIZE
def _tt_probe(h, depth, alpha, beta):
    e = _TT[h & TT_MASK]
    if e is None or e[0] != h:
        return (None, 0)
    _, ed, ef, es, em = e
    if ed >= depth:
        if ef == TT_EXACT:
            return (es, em)
        if ef == TT_LOWER and es >= beta:
            return (es, em)
        if ef == TT_UPPER and es <= alpha:
            return (es, em)
    return (None, em)
def _tt_store(h, depth, flag, score, move):
    idx = h & TT_MASK
    e = _TT[idx]
    if e is None or e[0] != h or e[1] <= depth or (e[1] == depth and flag == TT_EXACT and (e[2] != TT_EXACT)):
        _TT[idx] = (h, depth, flag, score, move)
_SEE_PA = PAWN_ATTACKS
_SEE_KA = KNIGHT_ATTACKS
_SEE_KGA = KING_ATTACKS
_SEE_BB = BB_SQUARES
_SEE_BT = _BISHOP_TABLE
_SEE_BMK = _BISHOP_MASKS
_SEE_RT = _ROOK_TABLE
_SEE_RMK = _ROOK_MASKS
_SEE_V = _SEE_VAL
def see(board, move: int) -> int:
    to = move >> 6 & 63
    fr = move & 63
    us = board.turn
    them = us ^ 1
    mt = move >> 12 & 15
    if mt == 5:
        gain0 = _SEE_V[P]
    else:
        cap_pc = move >> 19 & 7
        gain0 = _SEE_V[cap_pc] if cap_pc <= 5 else 0
    agg_pc = move >> 16 & 7
    occ = board.all_occ ^ _SEE_BB[fr]
    p = board.pieces
    p_copy = [p[0][0], p[0][1], p[0][2], p[0][3], p[0][4], p[0][5], p[1][0], p[1][1], p[1][2], p[1][3], p[1][4], p[1][5]]
    p_copy[us * 6 + agg_pc] ^= _SEE_BB[fr]
    gain = [0] * 32
    gain[0] = gain0
    d = 0
    side = them
    BT = _SEE_BT
    BMK = _SEE_BMK
    RT = _SEE_RT
    RMK = _SEE_RMK
    KA = _SEE_KA
    KGA = _SEE_KGA
    PA = _SEE_PA
    SV = _SEE_V
    while True:
        d += 1
        gain[d] = SV[agg_pc] - gain[d - 1]
        if -gain[d - 1] < 0 and gain[d] < 0:
            break
        base = side * 6
        lva_bb = 0
        agg_pc = -1
        att = PA[side ^ 1][to] & p_copy[base + P] & occ
        if att:
            lva_bb = att & -att
            agg_pc = P
        else:
            att = KA[to] & p_copy[base + N] & occ
            if att:
                lva_bb = att & -att
                agg_pc = N
            else:
                diag = BT[to][occ & BMK[to]]
                att = diag & p_copy[base + B] & occ
                if att:
                    lva_bb = att & -att
                    agg_pc = B
                else:
                    orth = RT[to][occ & RMK[to]]
                    att = orth & p_copy[base + R] & occ
                    if att:
                        lva_bb = att & -att
                        agg_pc = R
                    else:
                        att = (diag | orth) & p_copy[base + Q] & occ
                        if att:
                            lva_bb = att & -att
                            agg_pc = Q
                        else:
                            att = KGA[to] & p_copy[base + K] & occ
                            if att:
                                lva_bb = att & -att
                                agg_pc = K
        if agg_pc == -1:
            break
        occ ^= lva_bb
        p_copy[side * 6 + agg_pc] ^= lva_bb
        side ^= 1
    while d > 1:
        d -= 1
        gain[d - 1] = -max(-gain[d - 1], gain[d])
    return gain[0]
def _is_material_draw(board) -> bool:
    pw = board.pieces[WHITE]
    pb = board.pieces[BLACK]
    if pw[P] | pb[P] | pw[R] | pb[R] | pw[Q] | pb[Q]:
        return False
    w_minors = pw[N] | pw[B]
    b_minors = pb[N] | pb[B]
    wm = w_minors.bit_count()
    bm = b_minors.bit_count()
    total = wm + bm
    if total == 0:
        return True
    if total == 1:
        return True
    if wm == 1 and bm == 1 and (pw[N] == 0) and (pb[N] == 0):
        _DARK = 12273903644374837845
        wb_dark = bool(pw[B] & _DARK)
        bb_dark = bool(pb[B] & _DARK)
        if wb_dark == bb_dark:
            return True
    return False
def _pawnless_scale(board) -> int:
    if board.pieces[WHITE][P] or board.pieces[BLACK][P]:
        return 1
    pw = board.pieces[WHITE]
    pb = board.pieces[BLACK]
    if pw[R] or pw[Q] or pb[R] or pb[Q]:
        return 1
    w_n = pw[N].bit_count()
    w_b = pw[B].bit_count()
    b_n = pb[N].bit_count()
    b_b = pb[B].bit_count()
    w_minors = w_n + w_b
    b_minors = b_n + b_b
    if w_minors >= 2 and b_minors == 0:
        if w_n == 2 and w_b == 0:
            return 4
        return 1
    if b_minors >= 2 and w_minors == 0:
        if b_n == 2 and b_b == 0:
            return 4
        return 1
    total = w_minors + b_minors
    if total <= 2:
        return 2
    return 1
_MT_QUIET = 0 << 12
_MT_DBL = 1 << 12
_MT_KC = 2 << 12
_MT_QC = 3 << 12
_MT_EP = 5 << 12
_MT_MASK = 15 << 12
_PROMO_BONUS = (3000, 5000, 7000, 9000)
_MV_LOCAL = _MV
_PA_LOCAL = PAWN_ATTACKS
_SEE_GOOD_BASE = 60000
_SEE_BAD_BASE = -20000
def _make_cont_hist():
    return [[[0] * 64 for _ in range(6)] for _ in range(384)]
_MM = 15 << 12
_KC_M = 2 << 12
_QC_M = 3 << 12
_EP_M = 5 << 12
_DBL_M = 1 << 12
def _filter_and_score(raw_moves, board, k1, k2, hist, cont_hist, prev_pc: int, prev_to: int, cap_hist, counter_move: int, tt_move: int=0):
    us_occ = board.occ[board.turn]
    them_occ = board.occ[board.turn ^ 1]
    all_occ = board.all_occ
    FC = FLAG_CAPTURE
    FP = FLAG_PROMO
    PB = _PROMO_BONUS
    SGB = _SEE_GOOD_BASE
    SBB = _SEE_BAD_BASE
    PA = _PA_LOCAL
    turn = board.turn
    scored = []
    append = scored.append
    ch_row = cont_hist[prev_pc * 64 + prev_to] if prev_pc >= 0 else None
    cap_h = cap_hist[turn]
    for m in raw_moves:
        mt = m & _MM
        if mt == _KC_M or mt == _QC_M:
            sc = 10000000 if m == tt_move else 0
            append((sc, m))
            continue
        to_bb = 1 << (m >> 6 & 63)
        if us_occ & to_bb:
            continue
        if mt == 0 or mt == _DBL_M:
            if all_occ & to_bb:
                continue
        elif m & FC and mt != _EP_M:
            v = m >> 19 & 7
            if v > 5 or not them_occ & to_bb:
                continue
        if m == tt_move:
            sc = 10000000
        elif m & FP:
            bonus = PB[m >> 12 & 3]
            if m & FC:
                vv = m >> 19 & 7
                if vv <= 5:
                    bonus += _MV_LOCAL[vv]
            sc = 90000 + bonus
        elif m & FC:
            see_val = see(board, m)
            atk = m >> 16 & 7
            vic = m >> 19 & 7
            ch_bonus = cap_h[atk][vic] if vic <= 5 else 0
            if see_val >= 0:
                sc = SGB + see_val + ch_bonus // 4
            else:
                sc = SBB + see_val
        else:
            pc = m >> 16 & 7
            to = m >> 6 & 63
            h_val = hist[pc][to]
            ch_val = ch_row[pc][to] if ch_row is not None else 0
            base = h_val + ch_val
            if pc and PA[turn ^ 1][to] & board.pieces[turn ^ 1][0]:
                base -= 50
            if m == k1:
                sc = 70000
            elif m == k2:
                sc = 69000
            elif m == counter_move:
                sc = 68000
            else:
                sc = base
        append((sc, m))
    scored.sort(reverse=True)
    return [m for _, m in scored]
class Searcher:
    __slots__ = ('nodes', '_start_time', '_end_time', '_stop', '_killers', '_hist', '_cont_hist', '_cap_hist', '_counter_moves', '_score_stack', '_rep_counts', '_best_move_changes')
    def __init__(self):
        self.nodes = 0
        self._start_time = 0.0
        self._end_time = 0.0
        self._stop = False
        self._killers = [[0, 0] for _ in range(MAX_DEPTH + 10)]
        self._hist = [[[0] * 64 for _ in range(6)] for _ in range(2)]
        self._cont_hist = _make_cont_hist()
        self._cap_hist = [[[0] * 6 for _ in range(6)] for _ in range(2)]
        self._counter_moves = [[0] * 64 for _ in range(64)]
        self._score_stack = []
        self._rep_counts = {}
        self._best_move_changes = 0
    def _check_time(self):
        if not self._stop and self.nodes & 1023 == 0:
            if time.time() >= self._end_time:
                self._stop = True
    def _build_history_counts(self, board):
        self._rep_counts.clear()
        current_fen = board.to_fen()
        moves_to_replay = []
        while board._undo:
            moves_to_replay.append(board._undo[-1][0])
            board.unmake_move(board._undo[-1][0])
        h = _full_hash(board)
        self._rep_counts[h] = self._rep_counts.get(h, 0) + 1
        for move in reversed(moves_to_replay):
            board.make_move(move)
            h = _full_hash(board)
            self._rep_counts[h] = self._rep_counts.get(h, 0) + 1
        board.set_fen(current_fen)
    def _quiesce(self, board, alpha: int, beta: int, h: int, checkers: int=-1, pinned: int=-1) -> int:
        self.nodes += 1
        self._check_time()
        if self._stop:
            return 0
        if self._rep_counts.get(h, 0) >= 2:
            return 0
        if _is_material_draw(board):
            return 0
        _, tt_move = _tt_probe(h, 0, alpha, beta)
        sp = evaluate(board)
        hm = board.halfmove
        if hm >= 100:
            return 0
        if hm >= 80:
            sp = sp * (100 - hm) // 20
        if sp >= beta:
            return beta
        if sp > alpha:
            alpha = sp
        if checkers == -1:
            captures = generate_captures(board)
        else:
            captures = generate_captures_from_info(board, checkers, pinned)
        if not captures:
            return alpha
        in_check = bool(checkers) if checkers != -1 else False
        if len(captures) > 1:
            FP = FLAG_PROMO
            FC = FLAG_CAPTURE
            PB = _PROMO_BONUS
            mv = _MV_LOCAL
            SV = _SEE_VAL
            cap_h = self._cap_hist[board.turn]
            scored = []
            for m in captures:
                if m == tt_move:
                    scored.append((10000000, m))
                    continue
                if m & FP:
                    bonus = PB[m >> 12 & 3]
                    if m & FC:
                        v = m >> 19 & 7
                        if v <= 5:
                            bonus += mv[v]
                    scored.append((90000 + bonus, m))
                elif m & FC:
                    see_val = see(board, m)
                    if not in_check and see_val < 0:
                        continue
                    atk = m >> 16 & 7
                    vic = m >> 19 & 7
                    ch_b = cap_h[atk][vic] if vic <= 5 else 0
                    scored.append((see_val + ch_b // 8, m))
                else:
                    scored.append((0, m))
            if not scored:
                return alpha
            scored.sort(reverse=True)
            captures = [m for _, m in scored]
        else:
            m = captures[0]
            if m & FLAG_CAPTURE and (not in_check) and (not m & FLAG_PROMO):
                if see(board, m) < 0:
                    return alpha
        rep = self._rep_counts
        stack = self._score_stack
        SV = _SEE_VAL
        for move in captures:
            if self._stop:
                return 0
            if not in_check and move & FLAG_CAPTURE and (not move & FLAG_PROMO):
                cap_pc = move >> 19 & 7
                if cap_pc <= 5 and sp + SV[cap_pc] + 200 < alpha:
                    continue
            new_h = _delta_hash(board, move, h)
            rep[new_h] = rep.get(new_h, 0) + 1
            dw, db = _score_delta(board, move)
            w, bl = stack[-1]
            stack.append((w + dw, bl + db))
            board.make_move(move)
            score = -self._quiesce(board, -beta, -alpha, new_h)
            board.unmake_move(move)
            stack.pop()
            rep[new_h] -= 1
            if rep[new_h] <= 0:
                del rep[new_h]
            if self._stop:
                return 0
            if score >= beta:
                if move & FLAG_CAPTURE and (not move & FLAG_PROMO):
                    atk = move >> 16 & 7
                    vic = move >> 19 & 7
                    if vic <= 5:
                        ch = self._cap_hist[board.turn ^ 1]
                        ch[atk][vic] = min(ch[atk][vic] + 1, 30000)
                return beta
            if score > alpha:
                alpha = score
        return alpha
    def _negamax(self, board, depth: int, alpha: int, beta: int, ply: int, h: int, null_ok: bool, prev_fr: int=-1, prev_pc: int=-1, prev_to: int=0, is_singular: bool=False) -> int:
        self.nodes += 1
        self._check_time()
        if self._stop:
            return 0
        if alpha < -(MATE_SCORE - ply):
            alpha = -(MATE_SCORE - ply)
        if beta > MATE_SCORE - ply:
            beta = MATE_SCORE - ply
        if alpha >= beta:
            return alpha
        rep = self._rep_counts
        if rep.get(h, 0) >= 2:
            return 0
        if _is_material_draw(board):
            return 0
        tt_score, tt_move = _tt_probe(h, depth, alpha, beta)
        if tt_score is not None and (not is_singular):
            return tt_score
        if depth <= 0:
            score = self._quiesce(board, alpha, beta, h)
            sc = _pawnless_scale(board)
            if sc > 1:
                score = score // sc
            return score
        us = board.turn
        raw_moves, checkers, in_check = generate_legal_moves_ex(board)
        static_eval = evaluate(board)
        hm = board.halfmove
        if hm >= 100:
            if not in_check:
                return 0
        if hm >= 80:
            static_eval = static_eval * (100 - hm) // 20
        if not in_check and depth <= RAZOR_DEPTH and (static_eval + RAZOR_MARGIN[depth] < alpha) and (abs(alpha) < MATE_SCORE - 100):
            qsc = self._quiesce(board, alpha, beta, h)
            if qsc < alpha:
                return qsc
        if not in_check and depth <= RFP_MAX_D and (static_eval - RFP_MARGIN * depth >= beta) and (abs(beta) < MATE_SCORE - 100):
            return beta
        if not in_check and depth >= PROBCUT_MIN_D and (abs(beta) < MATE_SCORE - 100):
            pc_beta = beta + PROBCUT_BETA
            see_threshold = pc_beta - static_eval
            pc_raw, _, pc_in_check = generate_legal_moves_ex(board)
            for pc_move in pc_raw:
                if not pc_move & FLAG_CAPTURE:
                    continue
                if pc_move & FLAG_PROMO:
                    continue
                if see(board, pc_move) < see_threshold:
                    continue
                new_h = _delta_hash(board, pc_move, h)
                rep[new_h] = rep.get(new_h, 0) + 1
                dw2, db2 = _score_delta(board, pc_move)
                stack = self._score_stack
                w2, bl2 = stack[-1]
                stack.append((w2 + dw2, bl2 + db2))
                board.make_move(pc_move)
                pc_pc = pc_move >> 16 & 7
                pc_to = pc_move >> 6 & 63
                pc_sc = -self._negamax(board, depth - 4, -pc_beta, -pc_beta + 1, ply + 1, new_h, False, pc_move & 63, pc_pc, pc_to)
                board.unmake_move(pc_move)
                stack.pop()
                rep[new_h] -= 1
                if rep[new_h] <= 0:
                    del rep[new_h]
                if self._stop:
                    return 0
                if pc_sc >= pc_beta:
                    _tt_store(h, depth - 3, TT_LOWER, pc_sc, pc_move)
                    return pc_beta
        if null_ok and (not in_check) and (depth >= NMP_MIN_D) and (static_eval >= beta) and (board.pieces[us][Q] | board.pieces[us][R] | board.pieces[us][B] | board.pieces[us][N]):
            nmp_red = NMP_BASE_R + depth // 6 + min(3, (static_eval - beta) // 200)
            nmp_red = min(nmp_red, NMP_MAX_R, depth - 1)
            old_ep = board.ep_sq
            board.turn ^= 1
            board.ep_sq = -1
            nh = h ^ _ZT ^ _ZE[old_ep if old_ep != -1 else 64] ^ _ZE[64]
            rep[nh] = rep.get(nh, 0) + 1
            stack = self._score_stack
            stack.append(stack[-1])
            sc = -self._negamax(board, depth - 1 - nmp_red, -beta, -beta + 1, ply + 1, nh, False)
            stack.pop()
            board.turn ^= 1
            board.ep_sq = old_ep
            rep[nh] -= 1
            if rep[nh] <= 0:
                del rep[nh]
            if self._stop:
                return 0
            if sc >= beta:
                _tt_store(h, depth, TT_LOWER, beta, 0)
                return beta
        eff_depth = depth
        if depth >= IIR_MIN_D and tt_move == 0 and (not in_check):
            eff_depth = depth - 1
        counter_move = 0
        if prev_fr >= 0:
            counter_move = self._counter_moves[prev_fr][prev_to]
        k1, k2 = self._killers[ply]
        hist = self._hist[us]
        ch = self._cont_hist
        cap_hist = self._cap_hist
        moves = _filter_and_score(raw_moves, board, k1, k2, hist, ch, prev_pc, prev_to, cap_hist, counter_move, tt_move)
        if not moves:
            return -(MATE_SCORE - ply) if in_check else 0
        orig_alpha = alpha
        best_move = moves[0]
        best_score = -INF
        stack = self._score_stack
        w, bl = stack[-1]
        do_futility = not in_check and eff_depth <= FP_DEPTH and (abs(alpha) < MATE_SCORE - 100)
        fut_threshold = static_eval + FP_MARGIN[eff_depth] if do_futility else 0
        lmp_limit = LMP_BASE + eff_depth * eff_depth if not in_check and eff_depth < LMP_MAX_D else 9999
        quiet_count = 0
        for i, move in enumerate(moves):
            if self._stop:
                return 0
            is_cap = bool(move & FLAG_CAPTURE)
            is_pro = bool(move & FLAG_PROMO)
            pc = move >> 16 & 7
            to = move >> 6 & 63
            fr = move & 63
            if not is_cap and (not is_pro):
                quiet_count += 1
            if not is_cap and (not is_pro) and (quiet_count > lmp_limit) and (i > 0) and (hist[pc][to] <= 0):
                continue
            if do_futility and (not is_cap) and (not is_pro) and (fut_threshold < alpha) and (i > 0):
                continue
            if not in_check and is_cap and (not is_pro) and (eff_depth <= SEE_PRUNE_D) and (i > 0):
                if see(board, move) < -50 * eff_depth:
                    continue
            extension = 0
            if eff_depth >= SE_MIN_D and move == tt_move and (not is_singular) and (tt_move != 0) and (abs(tt_score if tt_score is not None else 0) < MATE_SCORE - 100):
                se_beta = max(alpha, (tt_score if tt_score is not None else static_eval) - SE_MARGIN)
                se_depth = eff_depth - 3 | 1
                se_score = self._negamax(board, se_depth, se_beta - 1, se_beta, ply, h, False, prev_fr, prev_pc, prev_to, is_singular=True)
                if self._stop:
                    return 0
                if se_score < se_beta:
                    extension = 1
            new_h = _delta_hash(board, move, h)
            rep[new_h] = rep.get(new_h, 0) + 1
            dw, db = _score_delta(board, move)
            stack.append((w + dw, bl + db))
            board.make_move(move)
            search_depth = eff_depth - 1 + extension
            if i >= LMR_MIN_M and search_depth >= LMR_MIN_D and (not is_cap) and (not is_pro) and (not in_check):
                red = max(1, int((search_depth ** 0.5 + (i - LMR_MIN_M) ** 0.5) * 0.45 + 0.5))
                if move == k1 or move == k2 or move == counter_move:
                    red = max(1, red - 1)
                elif hist[pc][to] < -2000:
                    red += 1
                red = min(red, search_depth - 1)
                score = -self._negamax(board, search_depth - red, -alpha - 1, -alpha, ply + 1, new_h, True, fr, pc, to)
                if self._stop:
                    board.unmake_move(move)
                    stack.pop()
                    rep[new_h] -= 1
                    if rep[new_h] <= 0:
                        del rep[new_h]
                    return 0
                if score > alpha:
                    score = -self._negamax(board, search_depth, -beta, -alpha, ply + 1, new_h, True, fr, pc, to)
            elif i > 0:
                score = -self._negamax(board, search_depth, -alpha - 1, -alpha, ply + 1, new_h, True, fr, pc, to)
                if self._stop:
                    board.unmake_move(move)
                    stack.pop()
                    rep[new_h] -= 1
                    if rep[new_h] <= 0:
                        del rep[new_h]
                    return 0
                if score > alpha:
                    score = -self._negamax(board, search_depth, -beta, -alpha, ply + 1, new_h, True, fr, pc, to)
            else:
                score = -self._negamax(board, search_depth, -beta, -alpha, ply + 1, new_h, True, fr, pc, to)
            board.unmake_move(move)
            stack.pop()
            rep[new_h] -= 1
            if rep[new_h] <= 0:
                del rep[new_h]
            if self._stop:
                return 0
            if score > best_score:
                best_score = score
                best_move = move
            if score > alpha:
                alpha = score
            if score >= beta:
                if not is_cap and (not is_pro):
                    self._killers[ply][1] = self._killers[ply][0]
                    self._killers[ply][0] = move
                    if prev_fr >= 0:
                        self._counter_moves[prev_fr][prev_to] = move
                    bonus = eff_depth * eff_depth
                    h_tbl = self._hist[us]
                    h_tbl[pc][to] += bonus
                    for j in range(i):
                        prev_m = moves[j]
                        if not prev_m & FLAG_CAPTURE and (not prev_m & FLAG_PROMO):
                            ppc = prev_m >> 16 & 7
                            pto = prev_m >> 6 & 63
                            h_tbl[ppc][pto] -= bonus
                    if h_tbl[pc][to] > 60000:
                        for pp in range(6):
                            row = h_tbl[pp]
                            for sq in range(64):
                                row[sq] >>= 1
                    if prev_pc >= 0:
                        idx = prev_pc * 64 + prev_to
                        v = ch[idx][pc][to] + bonus
                        ch[idx][pc][to] = v if v < 30000 else 30000
                else:
                    atk = move >> 16 & 7
                    vic = move >> 19 & 7
                    if vic <= 5:
                        cap_h = self._cap_hist[us]
                        cap_h[atk][vic] = min(cap_h[atk][vic] + eff_depth, 30000)
                _tt_store(h, eff_depth, TT_LOWER, beta, best_move)
                return beta
        flag = TT_EXACT if alpha > orig_alpha else TT_UPPER
        val = best_score if flag == TT_EXACT else alpha
        _tt_store(h, eff_depth, flag, val, best_move)
        return val
    def search(self, board, think_time_sec: float=2.0):
        self._stop = False
        self._start_time = time.time()
        self._end_time = self._start_time + think_time_sec
        self.nodes = 0
        self._best_move_changes = 0
        self._killers = [[0, 0] for _ in range(MAX_DEPTH + 10)]
        self._hist = [[[0] * 64 for _ in range(6)] for _ in range(2)]
        self._score_stack = [_full_score(board)]
        self._build_history_counts(board)
        if _is_material_draw(board):
            return (None, 0)
        raw_root = generate_legal_moves(board)
        k1, k2 = self._killers[0]
        hist = self._hist[board.turn]
        ch = self._cont_hist
        cap_hist = self._cap_hist
        root_moves = _filter_and_score(raw_root, board, k1, k2, hist, ch, -1, 0, cap_hist, 0)
        if not root_moves:
            return (None, 0)
        root_h = _full_hash(board)
        best_move = root_moves[0]
        best_score = evaluate(board)
        prev_best = best_move
        for depth in range(1, MAX_DEPTH + 1):
            if self._stop:
                break
            aw_lo = best_score - ASPIRATION if depth >= 2 else -INF
            aw_hi = best_score + ASPIRATION if depth >= 2 else INF
            aw_width = ASPIRATION
            depth_best_move = best_move
            depth_best_score = -INF
            while True:
                if self._stop:
                    break
                alpha = aw_lo
                depth_best_score = -INF
                depth_best_move = best_move
                k1, k2 = self._killers[0]
                _, ttm = _tt_probe(root_h, depth, aw_lo, aw_hi)
                root_moves = _filter_and_score(root_moves, board, k1, k2, hist, ch, -1, 0, cap_hist, 0, ttm)
                rep = self._rep_counts
                w, bl = self._score_stack[0]
                stack = self._score_stack
                for move in root_moves:
                    if self._stop:
                        break
                    self.nodes += 1
                    new_h = _delta_hash(board, move, root_h)
                    rep[new_h] = rep.get(new_h, 0) + 1
                    dw, db = _score_delta(board, move)
                    stack.append((w + dw, bl + db))
                    pc = move >> 16 & 7
                    to = move >> 6 & 63
                    fr = move & 63
                    board.make_move(move)
                    score = -self._negamax(board, depth - 1, -aw_hi, -alpha, 1, new_h, True, fr, pc, to)
                    board.unmake_move(move)
                    stack.pop()
                    rep[new_h] -= 1
                    if rep[new_h] <= 0:
                        del rep[new_h]
                    if self._stop:
                        break
                    if score > depth_best_score:
                        depth_best_score = score
                        depth_best_move = move
                    if score > alpha:
                        alpha = score
                if self._stop:
                    break
                if depth >= 2:
                    if depth_best_score <= aw_lo:
                        aw_width *= 4
                        aw_lo = max(-INF, depth_best_score - aw_width)
                    elif depth_best_score >= aw_hi:
                        aw_width *= 4
                        aw_hi = min(INF, depth_best_score + aw_width)
                    else:
                        break
                    if aw_lo <= -INF + 1 and aw_hi >= INF - 1:
                        break
                else:
                    break
            if not self._stop:
                best_move = depth_best_move
                best_score = depth_best_score
                if best_move != prev_best:
                    self._best_move_changes += 1
                    prev_best = best_move
            elapsed = time.time() - self._start_time
            remaining = self._end_time - time.time()
            if remaining <= 0:
                break
            if elapsed > think_time_sec * 0.6 and self._best_move_changes == 0 and depth >= 4:
                break
            if elapsed > think_time_sec * 0.5 and self._best_move_changes >= 3:
                self._end_time = min(self._start_time + think_time_sec * 2.0, self._end_time + think_time_sec * 0.5)
        return (best_move, best_score)
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
