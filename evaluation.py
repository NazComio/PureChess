from __future__ import annotations
from constants import P, N, B, R, Q, K, WHITE, BLACK, FULL_BOARD, KNIGHT_ATTACKS, KING_ATTACKS, PAWN_ATTACKS, BB_SQUARES, NOT_FILE_A, NOT_FILE_H, RANK_1, RANK_2, RANK_3, RANK_4, RANK_5, RANK_6, RANK_7, RANK_8, RAYS
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
    bishop_bb.bit_length() - 1
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
    board.occ[WHITE]
    board.occ[BLACK]
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
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        skip = skip_psqt_white if c == WHITE else skip_psqt_black
        pp = board.pieces[c]
        for pc in range(6):
            bb = pp[pc]
            mat_mg = MAT_MG[pc]
            mat_eg = MAT_EG[pc]
            psqt_tbl = PSQT[pc] if not skip else [0] * 64
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
                    can_castle = bool(board.castling & (1 if c == WHITE else 4 | 8))
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
                    if unsafe:
                        if unsafe & _BB_SQ[block_sq]:
                            k = 0
                        elif unsafe:
                            k = 9
                    else:
                        k = 20 if not unsafe else k
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
            sq // 8
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