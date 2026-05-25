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
