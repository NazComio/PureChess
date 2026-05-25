from __future__ import annotations
from constants import P, N, B, R, Q, K, WHITE, BLACK, FULL_BOARD, KNIGHT_ATTACKS, KING_ATTACKS, PAWN_ATTACKS, BB_SQUARES, NOT_FILE_A, NOT_FILE_H, RANK_1, RANK_2, RANK_3, RANK_4, RANK_5, RANK_6, RANK_7, RANK_8, RAYS
from moves import _BISHOP_TABLE, _BISHOP_MASKS, _ROOK_TABLE, _ROOK_MASKS
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
FLIP = [sq ^ 56 for sq in range(64)]
def _build_flat_pst():
    mg_w = [0] * (6 * 64)
    mg_b = [0] * (6 * 64)
    eg_w = [0] * (6 * 64)
    eg_b = [0] * (6 * 64)
    full_mg_w = [0] * (6 * 64)
    full_mg_b = [0] * (6 * 64)
    full_eg_w = [0] * (6 * 64)
    full_eg_b = [0] * (6 * 64)
    for pc in range(6):
        mat_mg = MAT_MG[pc]
        mat_eg = MAT_EG[pc]
        for sq in range(64):
            idx_w = sq
            idx_b = sq ^ 56
            packed_w = PSQT[pc][idx_w]
            packed_b = PSQT[pc][idx_b]
            m_w = _mg(packed_w); e_w = _eg(packed_w)
            m_b = _mg(packed_b); e_b = _eg(packed_b)
            base = pc * 64 + sq
            mg_w[base] = m_w;   eg_w[base] = e_w
            mg_b[base] = m_b;   eg_b[base] = e_b
            full_mg_w[base] = mat_mg + m_w;  full_eg_w[base] = mat_eg + e_w
            full_mg_b[base] = mat_mg + m_b;  full_eg_b[base] = mat_eg + e_b
    return (tuple(mg_w), tuple(mg_b), tuple(eg_w), tuple(eg_b),
            tuple(full_mg_w), tuple(full_mg_b), tuple(full_eg_w), tuple(full_eg_b))
PST_MG_W, PST_MG_B, PST_EG_W, PST_EG_B, _FULL_MG_W, _FULL_MG_B, _FULL_EG_W, _FULL_EG_B = _build_flat_pst()
def pst_score(piece_type: int, square: int, is_white: bool) -> tuple:
    idx = square if is_white else FLIP[square]
    packed = PSQT[piece_type][idx]
    return _mg(packed), _eg(packed)
_LSB_TABLE = {1 << i: i for i in range(64)}
_SQ_FILE = [sq & 7 for sq in range(64)]
_SQ_RANK = [sq >> 3 for sq in range(64)]
_SQ_BB = [1 << sq for sq in range(64)]
_MB_RAW = [[(-62, -81), (-53, -56), (-12, -30), (-4, -14), (3, 8), (13, 15), (22, 23), (28, 27), (33, 33)], [(-48, -59), (-20, -23), (16, -3), (26, 13), (38, 24), (51, 42), (55, 54), (63, 57), (63, 65), (68, 73), (81, 78), (81, 86), (91, 88), (98, 97)], [(-58, -76), (-27, -18), (-15, 28), (-10, 55), (-5, 69), (-2, 82), (9, 112), (16, 118), (30, 132), (29, 142), (32, 155), (38, 165), (46, 166), (48, 169), (58, 171)], [(-39, -36), (-21, -15), (3, 8), (3, 18), (14, 34), (22, 54), (28, 61), (41, 73), (43, 79), (48, 92), (56, 94), (60, 104), (60, 113), (66, 120), (67, 123), (70, 126), (71, 133), (73, 136), (79, 140), (88, 143), (88, 148), (99, 166), (102, 170), (102, 175), (106, 184), (109, 191), (113, 206), (116, 212)]]
MOBILITY_BONUS = tuple((tuple((_S(mg, eg) for mg, eg in arr)) for arr in _MB_RAW))
_MOB_MAX = (8, 13, 14, 27)
_MOB_MG = tuple(tuple(_mg(s) for s in row) for row in MOBILITY_BONUS)
_MOB_EG = tuple(tuple(_eg(s) for s in row) for row in MOBILITY_BONUS)
PASSED_RANK = (_S(0,0), _S(10,28), _S(17,33), _S(15,41), _S(62,72), _S(168,177), _S(276,260), _S(0,0))
_PR_MG = tuple(_mg(s) for s in PASSED_RANK)
_PR_EG = tuple(_eg(s) for s in PASSED_RANK)
_BISHOP_PAWNS = _S(3,7);      _BP_MG = _mg(_BISHOP_PAWNS);  _BP_EG = _eg(_BISHOP_PAWNS)
_BISHOP_PAIR  = _S(37,65);    _BPAIR_MG = _mg(_BISHOP_PAIR); _BPAIR_EG = _eg(_BISHOP_PAIR)
_LONG_DIAGONAL_BISHOP = _S(45,0); _LDB_MG = _mg(_LONG_DIAGONAL_BISHOP); _LDB_EG = _eg(_LONG_DIAGONAL_BISHOP)
_MINOR_BEHIND_PAWN = _S(18,3); _MBP_MG = _mg(_MINOR_BEHIND_PAWN); _MBP_EG = _eg(_MINOR_BEHIND_PAWN)
_OUTPOST = _S(30,21);         _OP_MG = _mg(_OUTPOST);        _OP_EG = _eg(_OUTPOST)
_REACHABLE_OUTPOST = _S(32,10); _ROP_MG = _mg(_REACHABLE_OUTPOST); _ROP_EG = _eg(_REACHABLE_OUTPOST)
_KING_PROTECTOR = _S(7,8);    _KP_MG = _mg(_KING_PROTECTOR); _KP_EG = _eg(_KING_PROTECTOR)
_ROOK_ON_OPEN_FILE = _S(47,25); _ROF_MG = _mg(_ROOK_ON_OPEN_FILE); _ROF_EG = _eg(_ROOK_ON_OPEN_FILE)
_ROOK_ON_SEMI_FILE = _S(21,4); _RSF_MG = _mg(_ROOK_ON_SEMI_FILE); _RSF_EG = _eg(_ROOK_ON_SEMI_FILE)
_ROOK_ON_QUEEN_FILE = _S(7,6); _RQF_MG = _mg(_ROOK_ON_QUEEN_FILE); _RQF_EG = _eg(_ROOK_ON_QUEEN_FILE)
_TRAPPED_ROOK = _S(52,10);    _TR_MG = _mg(_TRAPPED_ROOK);  _TR_EG = _eg(_TRAPPED_ROOK)
_WEAK_QUEEN = _S(49,15)
_PASSED_FILE_PENALTY = _S(11,8); _PFP_MG = _mg(_PASSED_FILE_PENALTY); _PFP_EG = _eg(_PASSED_FILE_PENALTY)
_ISOLATED_PAWN = _S(15,9);    _ISO_MG = _mg(_ISOLATED_PAWN); _ISO_EG = _eg(_ISOLATED_PAWN)
_DOUBLED_PAWN = _S(11,8);     _DBL_MG = _mg(_DOUBLED_PAWN);  _DBL_EG = _eg(_DOUBLED_PAWN)
_ISOLATED_DOUBLED = _S(25,18); _ID_MG = _mg(_ISOLATED_DOUBLED); _ID_EG = _eg(_ISOLATED_DOUBLED)
_PAWN_CHAIN = _S(6,4);        _CHN_MG = _mg(_PAWN_CHAIN);    _CHN_EG = _eg(_PAWN_CHAIN)
_BACKWARD_PAWN = _S(17,10);   _BKWD_MG = _mg(_BACKWARD_PAWN); _BKWD_EG = _eg(_BACKWARD_PAWN)
_PHALANX = _S(12,7);          _PH_MG = _mg(_PHALANX);        _PH_EG = _eg(_PHALANX)
_CANDIDATE_PASSED = _S(18,24); _CP_MG = _mg(_CANDIDATE_PASSED); _CP_EG = _eg(_CANDIDATE_PASSED)
_ROOK_ON_SEVENTH = _S(23,11); _R7_MG = _mg(_ROOK_ON_SEVENTH); _R7_EG = _eg(_ROOK_ON_SEVENTH)
_ROOK_BATTERY = _S(12,6);     _RB_MG = _mg(_ROOK_BATTERY);   _RB_EG = _eg(_ROOK_BATTERY)
_QUEEN_ROOK_BATTERY = _S(8,4)
_BAD_BISHOP_BLOCKED = _S(5,0)
_KNIGHT_OUTPOST_PERM = _S(16,8); _NOP_MG = _mg(_KNIGHT_OUTPOST_PERM); _NOP_EG = _eg(_KNIGHT_OUTPOST_PERM)
_CENTER_CONTROL_MINOR = _S(4,2); _CCM_MG = _mg(_CENTER_CONTROL_MINOR); _CCM_EG = _eg(_CENTER_CONTROL_MINOR)
_MOPUP_RANK = _S(0,5); _MOPUP_DIST = _S(0,4)
_ENEMY_KING_EDGE_PST = [90,80,70,60,60,70,80,90,80,60,50,40,40,50,60,80,70,50,30,20,20,30,50,70,60,40,20,10,10,20,40,60,60,40,20,10,10,20,40,60,70,50,30,20,20,30,50,70,80,60,50,40,40,50,60,80,90,80,70,60,60,70,80,90]
_ENEMY_KING_CORNER_PST = [100,85,70,55,55,70,85,100,85,60,45,30,30,45,60,85,70,45,25,12,12,25,45,70,55,30,12,0,0,12,30,55,55,30,12,0,0,12,30,55,70,45,25,12,12,25,45,70,85,60,45,30,30,45,60,85,100,85,70,55,55,70,85,100]
_MOPUP_PROXIMITY_BONUS = 30; _MOPUP_EDGE_SCALE = 4; _MOPUP_CORNER_SCALE = 5; _MOPUP_PROXIMITY_SCALE = 10
_XRAY_ATTACK = _S(4,2);       _XR_MG = _mg(_XRAY_ATTACK);    _XR_EG = _eg(_XRAY_ATTACK)
_SAFE_CHECK = _S(20,8)
_PAWN_STORM = _S(9,0);        _PS_MG = _mg(_PAWN_STORM)
_KING_SHELTER = _S(14,0);     _KSH_MG = _mg(_KING_SHELTER)
_HANGING = _S(30,18);         _HNG_MG = _mg(_HANGING);        _HNG_EG = _eg(_HANGING)
_THREAT_BY_KING = _S(16,50);  _TBK_MG = _mg(_THREAT_BY_KING); _TBK_EG = _eg(_THREAT_BY_KING)
_THREAT_BY_PAWN_PUSH = _S(20,16); _TBPP_MG = _mg(_THREAT_BY_PAWN_PUSH); _TBPP_EG = _eg(_THREAT_BY_PAWN_PUSH)
_THREAT_BY_SAFE_PAWN = _S(55,35); _TBSP_MG = _mg(_THREAT_BY_SAFE_PAWN); _TBSP_EG = _eg(_THREAT_BY_SAFE_PAWN)
_PAWNLESS_FLANK = _S(17,95);  _PLF_MG = _mg(_PAWNLESS_FLANK); _PLF_EG = _eg(_PAWNLESS_FLANK)
_FLANK_ATTACKS = _S(8,0);     _FA_MG = _mg(_FLANK_ATTACKS)
_TEMPO = 28
_ROOK_BEHIND_PASSED_MG = 16
_ROOK_BEHIND_PASSED_EG = 38
_ISLAND_PENALTY_MG = 8
_ISLAND_PENALTY_EG = 12
_KING_CENTRAL_MG = 0
_KING_CENTRAL_EG = 6
_BISHOP_OPEN_MG = 12
_BISHOP_OPEN_EG = 22
_TROPISM_MG = 0
_TROPISM_EG = 3
_THREAT_BY_MINOR = (_S(0,0),_S(5,20),_S(35,25),_S(45,32),_S(55,65),_S(45,90))
_THREAT_BY_ROOK  = (_S(0,0),_S(2,28),_S(22,42),_S(22,38),_S(0,24),_S(28,22))
_TBM_MG = tuple(_mg(s) for s in _THREAT_BY_MINOR)
_TBM_EG = tuple(_eg(s) for s in _THREAT_BY_MINOR)
_TBR_MG = tuple(_mg(s) for s in _THREAT_BY_ROOK)
_TBR_EG = tuple(_eg(s) for s in _THREAT_BY_ROOK)
_KING_ATK_WEIGHT = (0, 0, 81, 52, 44, 10)
_QUEEN_SAFE_CHECK = 780; _ROOK_SAFE_CHECK = 1080; _BISHOP_SAFE_CHECK = 635; _KNIGHT_SAFE_CHECK = 790
_SPACE_THRESHOLD = 5000
FILE_BB = tuple(sum(1 << r*8+f for r in range(8)) for f in range(8))
_QUEENSIDE_MAP = (0, 1, 2, 3, 3, 2, 1, 0)
RANK_BB = (RANK_1, RANK_2, RANK_3, RANK_4, RANK_5, RANK_6, RANK_7, RANK_8)
_BELOW_RANK = tuple(sum(RANK_BB[i] for i in range(r)) for r in range(8))
_ABOVE_RANK = tuple(sum(RANK_BB[i] for i in range(r+1, 8)) for r in range(8))
_OUTPOST_RANKS = (RANK_4 | RANK_5 | RANK_6, RANK_5 | RANK_4 | RANK_3)
_LOW_RANKS = (RANK_2 | RANK_3, RANK_7 | RANK_6)
CENTER_FILES = FILE_BB[2] | FILE_BB[3] | FILE_BB[4] | FILE_BB[5]
QUEEN_SIDE = FILE_BB[0] | FILE_BB[1] | FILE_BB[2] | FILE_BB[3]
KING_SIDE  = FILE_BB[4] | FILE_BB[5] | FILE_BB[6] | FILE_BB[7]
CENTER_4SQ = 1<<27 | 1<<28 | 1<<35 | 1<<36
_SPACE_MASK_W = CENTER_FILES & (RANK_2 | RANK_3 | RANK_4)
_SPACE_MASK_B = CENTER_FILES & (RANK_7 | RANK_6 | RANK_5)
def _build_king_flanks():
    flanks = []
    for f in range(8):
        bb = 0
        for ff in range(max(0,f-1), min(7,f+1)+1):
            bb |= FILE_BB[ff]
        flanks.append(bb)
    return tuple(flanks)
KING_FLANK = _build_king_flanks()
def _build_dist():
    d = [[0]*64 for _ in range(64)]
    for a in range(64):
        for b in range(64):
            d[a][b] = max(abs(a//8-b//8), abs(a%8-b%8))
    return d
_DIST = _build_dist()
_DARK_SQ = sum(1<<r*8+f for r in range(8) for f in range(8) if (r+f)%2==1)
_LIGHT_SQ = FULL_BOARD ^ _DARK_SQ
_BB_SQ = BB_SQUARES
_KA = KNIGHT_ATTACKS
_KING_A = KING_ATTACKS
_PA = PAWN_ATTACKS
_NFA = NOT_FILE_A
_NFH = NOT_FILE_H
_BT = _BISHOP_TABLE
_BMK = _BISHOP_MASKS
_RT = _ROOK_TABLE
_RMK = _ROOK_MASKS
_popcount = int.bit_count
def _pawn_attacks_white(pawns: int) -> int:
    return ((pawns & _NFH) << 9 | (pawns & _NFA) << 7) & FULL_BOARD
def _pawn_attacks_black(pawns: int) -> int:
    return (pawns & _NFA) >> 7 | (pawns & _NFH) >> 9
def _passed_pawns_white(wpawns: int, bpawns: int) -> int:
    bp = bpawns | (bpawns & _NFA) >> 7 | (bpawns & _NFH) >> 9
    span = bp | bp>>8 | bp>>16 | bp>>24 | bp>>32 | bp>>40 | bp>>48
    return wpawns & ~span
def _passed_pawns_black(bpawns: int, wpawns: int) -> int:
    wp = wpawns | (wpawns & _NFH) << 9 | (wpawns & _NFA) << 7
    span = (wp | wp<<8 | wp<<16 | wp<<24 | wp<<32 | wp<<40 | wp<<48) & FULL_BOARD
    return bpawns & ~span
def _king_ring(ksq: int) -> int:
    f = max(1, min(6, _SQ_FILE[ksq]))
    r = max(1, min(6, _SQ_RANK[ksq]))
    clamped = r * 8 + f
    return _KING_A[clamped] | _SQ_BB[clamped]
_NPM_WEIGHT = (0, 337, 365, 477, 1025, 0)
def _non_pawn_material(board) -> int:
    total = 0
    w = board.pieces[WHITE]
    b = board.pieces[BLACK]
    for pc in (N, B, R, Q):
        total += _NPM_WEIGHT[pc] * (_popcount(w[pc]) + _popcount(b[pc]))
    return total
def _has_mating_material(board, side: int) -> bool:
    opp = side ^ 1
    if board.pieces[opp][P] or board.pieces[opp][N] or board.pieces[opp][B] or board.pieces[opp][R] or board.pieces[opp][Q]:
        return False
    queens = board.pieces[side][Q]; rooks = board.pieces[side][R]
    bishops = board.pieces[side][B]; knights = board.pieces[side][N]
    if queens or rooks: return True
    if _popcount(bishops) >= 2: return True
    if bishops and knights: return True
    return False
def _is_kbnk(board):
    for side in (WHITE, BLACK):
        opp = side ^ 1
        if board.pieces[side][P]|board.pieces[side][R]|board.pieces[side][Q]|board.pieces[opp][P]|board.pieces[opp][R]|board.pieces[opp][Q]|board.pieces[opp][N]|board.pieces[opp][B]:
            continue
        if board.pieces[side][N].bit_count()==1 and board.pieces[side][B].bit_count()==1 and not board.pieces[side][Q] and not board.pieces[opp][N] and not board.pieces[opp][B]:
            return (side, opp)
    return None
def _is_knnkp(board):
    for side in (WHITE, BLACK):
        opp = side ^ 1
        if board.pieces[side][P]|board.pieces[side][R]|board.pieces[side][Q]|board.pieces[side][B]|board.pieces[opp][R]|board.pieces[opp][Q]|board.pieces[opp][N]|board.pieces[opp][B]:
            continue
        if board.pieces[side][N].bit_count()==2 and not board.pieces[side][Q] and not board.pieces[opp][N] and board.pieces[opp][P].bit_count()==1:
            pawn_bb = board.pieces[opp][P]
            pawn_sq = _LSB_TABLE[pawn_bb & -pawn_bb]
            return (side, opp, pawn_sq)
    return None
_TROITZKY_WHITE = {0:3,1:5,2:4,3:3,4:3,5:4,6:5,7:3}
_TROITZKY_BLACK = {0:4,1:2,2:3,3:4,4:4,5:3,6:2,7:4}
def _troitzky_win_possible(defender_color: int, pawn_sq: int) -> bool:
    file = pawn_sq & 7
    if defender_color == WHITE: return pawn_sq >> 3 <= _TROITZKY_WHITE[file]
    else: return pawn_sq >> 3 >= _TROITZKY_BLACK[file]
def _eval_kbnk(board, winner: int, loser: int) -> int:
    bishop_bb = board.pieces[winner][B]
    bishop_is_dark = bool(bishop_bb & _DARK_SQ)
    ek_sq = _LSB_TABLE[board.pieces[loser][K] & -board.pieces[loser][K]]
    ok_sq = _LSB_TABLE[board.pieces[winner][K] & -board.pieces[winner][K]]
    correct_corners = (1<<56 | 1<<7) if bishop_is_dark else (1<<0 | 1<<63)
    def cheb(a, b): return max(abs(_SQ_RANK[a]-_SQ_RANK[b]), abs(_SQ_FILE[a]-_SQ_FILE[b]))
    best_dist = 7
    tmp = correct_corners
    while tmp:
        lsb = tmp & -tmp
        corner = _LSB_TABLE[lsb]
        d = cheb(ek_sq, corner)
        if d < best_dist: best_dist = d
        tmp ^= lsb
    score = 800 - 40*best_dist + (7-cheb(ok_sq,ek_sq))*10
    knight_sq = _LSB_TABLE[board.pieces[winner][N] & -board.pieces[winner][N]]
    score += (5-cheb(knight_sq,ek_sq))*5
    wrong_corners = (1<<56|1<<7) if not bishop_is_dark else (1<<0|1<<63)
    if 1<<ek_sq & wrong_corners: score -= 200
    if best_dist==0 and cheb(ok_sq,ek_sq)<=2: score += 2000
    return score
def _eval_knnkp(board, attacker: int, defender: int, pawn_sq: int) -> int:
    if not _troitzky_win_possible(defender, pawn_sq): return 0
    ek_sq = _LSB_TABLE[board.pieces[defender][K] & -board.pieces[defender][K]]
    ok_sq = _LSB_TABLE[board.pieces[attacker][K] & -board.pieces[attacker][K]]
    block_sq = pawn_sq + (8 if defender==WHITE else -8)
    knight_bb = board.pieces[attacker][N]
    block_score = 500 if knight_bb & _SQ_BB[block_sq] else 0
    king_pawn_dist = max(abs(_SQ_RANK[ok_sq]-_SQ_RANK[pawn_sq]), abs(_SQ_FILE[ok_sq]-_SQ_FILE[pawn_sq]))
    capture_risk = -300 if king_pawn_dist<=1 and not knight_bb&_SQ_BB[block_sq] else 0
    edge_rank = _SQ_RANK[ek_sq]==0 or _SQ_RANK[ek_sq]==7
    edge_file = _SQ_FILE[ek_sq]==0 or _SQ_FILE[ek_sq]==7
    edge_bonus = (50 if edge_rank else 0) + (50 if edge_file else 0)
    corner_bonus = 200 if edge_rank and edge_file else 0
    king_dist = max(abs(_SQ_RANK[ok_sq]-_SQ_RANK[ek_sq]), abs(_SQ_FILE[ok_sq]-_SQ_FILE[ek_sq]))
    score = block_score + capture_risk + edge_bonus + corner_bonus + (7-king_dist)*10 + 300
    pawn_rank = pawn_sq>>3 if defender==WHITE else 7-(pawn_sq>>3)
    if pawn_rank > 4: score -= 20*(pawn_rank-4)
    return score
_PAWN_HASH_SIZE = 1 << 14
_PAWN_HASH_MASK = _PAWN_HASH_SIZE - 1
_pawn_hash = [None] * _PAWN_HASH_SIZE
def _pawn_hash_key(wp: int, bp: int) -> int:
    return (wp ^ bp * 0x9E3779B97F4A7C15) & _PAWN_HASH_MASK
def _eval_pawn_structure(wp: int, bp: int):
    mg = eg = 0
    NFA = _NFA; NFH = _NFH; FB = FILE_BB; FBB = FULL_BOARD
    w_passed = _passed_pawns_white(wp, bp)
    b_passed = _passed_pawns_black(bp, wp)
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        own = wp if c == WHITE else bp
        them = bp if c == WHITE else wp
        if not own: continue
        shifted = (own & NFH) << 1 | (own & NFA) >> 1
        ph_count = _popcount(own & shifted) // 2
        mg += sign * _PH_MG * ph_count
        eg += sign * _PH_EG * ph_count
        if c == WHITE:
            defenders = (own & NFH) >> 9 | (own & NFA) >> 7
        else:
            defenders = (own & NFA) << 7 | (own & NFH) << 9
        chain_count = _popcount(own & defenders & FBB)
        mg += sign * _CHN_MG * chain_count
        eg += sign * _CHN_EG * chain_count
        for f in range(8):
            pawns_on_file = own & FB[f]
            if not pawns_on_file: continue
            count = _popcount(pawns_on_file)
            adj = 0
            if f > 0: adj |= own & FB[f-1]
            if f < 7: adj |= own & FB[f+1]
            is_isolated = not adj
            if is_isolated:
                mg -= sign * _ISO_MG * count
                eg -= sign * _ISO_EG * count
            if count > 1:
                mg -= sign * _DBL_MG * (count-1)
                eg -= sign * _DBL_EG * (count-1)
                if is_isolated:
                    mg -= sign * _ID_MG * (count-1)
                    eg -= sign * _ID_EG * (count-1)
        them_pawns = them
        tmp = own
        while tmp:
            lsb = tmp & -tmp
            sq = _LSB_TABLE[lsb]
            tmp ^= lsb
            f = _SQ_FILE[sq]
            stop = sq + 8 if c == WHITE else sq - 8
            if stop < 0 or stop > 63: continue
            behind_mask = (1 << sq) - 1 if c == WHITE else (FBB ^ (1 << sq+1) - 1) & FBB
            if own & FB[f] & behind_mask: continue
            adj_sup = 0
            if f > 0: adj_sup |= own & FB[f-1]
            if f < 7: adj_sup |= own & FB[f+1]
            if not adj_sup: continue
            if not PAWN_ATTACKS[c][stop] & them_pawns: continue
            mg -= sign * _BKWD_MG
            eg -= sign * _BKWD_EG
        if not own or not them: continue
        for f in range(8):
            if not own & FB[f]: continue
            own_helpers = _popcount(own & ((FB[f-1] if f>0 else 0)|(FB[f+1] if f<7 else 0)))
            them_helpers = _popcount(them & ((FB[f-1] if f>0 else 0)|(FB[f+1] if f<7 else 0)))
            them_on_file = _popcount(them & FB[f])
            if them_on_file > 0 and own_helpers > them_helpers:
                mg += sign * _CP_MG
                eg += sign * _CP_EG
    for c2 in (WHITE, BLACK):
        sign2 = 1 if c2 == WHITE else -1
        own2 = wp if c2 == WHITE else bp
        if not own2:
            continue
        islands = 0
        in_isl = False
        for fi in range(8):
            if own2 & FILE_BB[fi]:
                if not in_isl:
                    islands += 1
                    in_isl = True
            else:
                in_isl = False
        if islands > 1:
            mg -= sign2 * _ISLAND_PENALTY_MG * (islands - 1)
            eg -= sign2 * _ISLAND_PENALTY_EG * (islands - 1)
    return mg, eg, w_passed, b_passed
def evaluate(board) -> int:
    mg_score = board.mg_score
    eg_score = board.eg_score
    phase = board.phase_total
    if phase > PHASE_MAX: phase = PHASE_MAX
    pW = board.pieces[WHITE]
    pB = board.pieces[BLACK]
    if _popcount(pW[B]) >= 2:
        mg_score += _BPAIR_MG
        eg_score += _BPAIR_EG
    if _popcount(pB[B]) >= 2:
        mg_score -= _BPAIR_MG
        eg_score -= _BPAIR_EG
    lazy_score = (mg_score * phase + eg_score * (PHASE_MAX - phase)) // PHASE_MAX
    if lazy_score > _LAZY_THRESHOLD or lazy_score < -_LAZY_THRESHOLD:
        result = lazy_score + _TEMPO
        return result if board.turn == WHITE else -result
    wp = pW[P]; bp = pB[P]
    ph_key = _pawn_hash_key(wp, bp)
    ph_entry = _pawn_hash[ph_key]
    if ph_entry is not None and ph_entry[0] == wp and ph_entry[1] == bp:
        _, _, pawn_mg, pawn_eg, w_passed, b_passed = ph_entry
    else:
        pawn_mg, pawn_eg, w_passed, b_passed = _eval_pawn_structure(wp, bp)
        _pawn_hash[ph_key] = (wp, bp, pawn_mg, pawn_eg, w_passed, b_passed)
    mg_score += pawn_mg
    eg_score += pawn_eg
    w_pawn_atk = _pawn_attacks_white(wp)
    b_pawn_atk = _pawn_attacks_black(bp)
    wps = wp
    NFH_local = _NFH
    NFA_local = _NFA
    wps |= ((wps & NFH_local) << 9 | (wps & NFA_local) << 7) & FULL_BOARD
    for _ in range(6):
        wps |= (wps & NFH_local) << 9 & FULL_BOARD | (wps & NFA_local) << 7 & FULL_BOARD
    w_pawn_span = wps
    bps = bp
    for _ in range(6):
        bps |= (bps & NFA_local) >> 7 | (bps & NFH_local) >> 9
    b_pawn_span = bps
    ALL = 6
    atk = [[0]*7, [0]*7]
    atk2 = [0,0]
    occ = board.all_occ
    wksq = _LSB_TABLE[pW[K] & -pW[K]]
    bksq = _LSB_TABLE[pB[K] & -pB[K]]
    atk[WHITE][K] = _KING_A[wksq]
    atk[BLACK][K] = _KING_A[bksq]
    atk[WHITE][P] = w_pawn_atk
    atk[BLACK][P] = b_pawn_atk
    for c in (WHITE, BLACK):
        atk[c][ALL] = atk[c][K] | atk[c][P]
        own = wp if c == WHITE else bp
        pp2 = own & (own - 1)
        dbl = (_pawn_attacks_white(pp2) if c == WHITE else _pawn_attacks_black(pp2)) if pp2 else 0
        atk2[c] = (atk[c][K] & atk[c][P]) | dbl
    w_king_ring = _king_ring(wksq)
    b_king_ring = _king_ring(bksq)
    wpp2 = wp & (wp-1); bpp2 = bp & (bp-1)
    if wpp2: w_king_ring &= ~_pawn_attacks_white(wpp2)
    if bpp2: b_king_ring &= ~_pawn_attacks_black(bpp2)
    ka_count = [0,0]
    ka_weight = [0,0]
    ka_atk = [0,0]
    low_w = _LOW_RANKS[WHITE]; low_b = _LOW_RANKS[BLACK]
    mob_area_w = ~((wp & (occ>>8 | low_w)) | pW[K] | pW[Q] | b_pawn_atk) & FULL_BOARD
    mob_area_b = ~((bp & ((occ<<8)&FULL_BOARD | low_b)) | pB[K] | pB[Q] | w_pawn_atk) & FULL_BOARD
    mob_area = [mob_area_w, mob_area_b]
    mob_mg = [0,0]; mob_eg = [0,0]
    piece_mg = 0; piece_eg = 0
    BT = _BT; BMK = _BMK; RT = _RT; RMK = _RMK
    KA = _KA; KING_A = _KING_A
    BB = _SQ_BB
    MOB_MG = _MOB_MG; MOB_EG = _MOB_EG
    MOB_MAX = _MOB_MAX
    DIST = _DIST
    KAW = _KING_ATK_WEIGHT
    OUTPOST_RANKS = _OUTPOST_RANKS
    NFA = _NFA; NFH = _NFH
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        them = c ^ 1
        pp = board.pieces[c]
        ppt = board.pieces[them]
        ksq_us = wksq if c == WHITE else bksq
        eks = bksq if c == WHITE else wksq
        their_ring = b_king_ring if c == WHITE else w_king_ring
        m_area = mob_area[c]
        op_ranks = OUTPOST_RANKS[c]
        own_patk = w_pawn_atk if c == WHITE else b_pawn_atk
        enem_span = b_pawn_span if c == WHITE else w_pawn_span
        bb = pp[N]
        atk[c][N] = 0
        while bb:
            lsb = bb & -bb
            sq = _LSB_TABLE[lsb]
            bb ^= lsb
            a = KA[sq]
            atk[c][N] |= a
            atk2[c] |= atk[c][ALL] & a
            atk[c][ALL] |= a
            if a & their_ring:
                ka_count[c] += 1
                ka_weight[c] += KAW[N]
                ka_atk[c] += _popcount(a & KING_A[eks])
            mob = _popcount(a & m_area)
            if mob > MOB_MAX[0]: mob = MOB_MAX[0]
            mob_mg[c] += MOB_MG[0][mob]
            mob_eg[c] += MOB_EG[0][mob]
            sq_bb = BB[sq]
            if sq_bb & op_ranks & own_patk & ~enem_span:
                piece_mg += sign * _OP_MG * 2
                piece_eg += sign * _OP_EG * 2
            elif a & ~pp[K] & ~pp[Q] & ~pp[N] & ~pp[B] & ~pp[R] & ~pp[P] & op_ranks & own_patk & ~enem_span:
                piece_mg += sign * _ROP_MG
                piece_eg += sign * _ROP_EG
            push = sq_bb << 8 if c == WHITE else sq_bb >> 8
            if push & (wp | bp):
                piece_mg += sign * _MBP_MG
                piece_eg += sign * _MBP_EG
            d = DIST[sq][ksq_us]
            piece_mg -= sign * _KP_MG * d
            piece_eg -= sign * _KP_EG * d
        bb = pp[B]
        atk[c][B] = 0
        xocc_b = occ ^ pp[Q]
        while bb:
            lsb = bb & -bb
            sq = _LSB_TABLE[lsb]
            bb ^= lsb
            a = BT[sq][xocc_b & BMK[sq]]
            atk[c][B] |= a
            atk2[c] |= atk[c][ALL] & a
            atk[c][ALL] |= a
            if a & their_ring:
                ka_count[c] += 1
                ka_weight[c] += KAW[B]
                ka_atk[c] += _popcount(a & KING_A[eks])
            mob = _popcount(a & m_area)
            if mob > MOB_MAX[1]: mob = MOB_MAX[1]
            mob_mg[c] += MOB_MG[1][mob]
            mob_eg[c] += MOB_EG[1][mob]
            sq_bb = BB[sq]
            if sq_bb & op_ranks & own_patk & ~enem_span:
                piece_mg += sign * _OP_MG
                piece_eg += sign * _OP_EG
            push = sq_bb << 8 if c == WHITE else sq_bb >> 8
            if push & (wp | bp):
                piece_mg += sign * _MBP_MG
                piece_eg += sign * _MBP_EG
            piece_mg -= sign * _KP_MG * DIST[sq][ksq_us]
            piece_eg -= sign * _KP_EG * DIST[sq][ksq_us]
            color_sq = _DARK_SQ if sq_bb & _DARK_SQ else _LIGHT_SQ
            n_same = _popcount(pp[P] & color_sq)
            blk_ctr = _popcount((wp if c==WHITE else bp) & ((occ>>8 if c==WHITE else (occ<<8)&FULL_BOARD) & CENTER_FILES))
            piece_mg -= sign * _BP_MG * n_same * (1 + blk_ctr)
            piece_eg -= sign * _BP_EG * n_same * (1 + blk_ctr)
            center_bb = BB[27]|BB[28]|BB[35]|BB[36]
            if _popcount(BT[sq][(wp|bp) & BMK[sq]] & center_bb) >= 2:
                piece_mg += sign * _LDB_MG
                piece_eg += sign * _LDB_EG
        bb = pp[R]
        atk[c][R] = 0
        xocc_r = occ ^ pp[Q] ^ pp[R]
        while bb:
            lsb = bb & -bb
            sq = _LSB_TABLE[lsb]
            bb ^= lsb
            a = RT[sq][xocc_r & RMK[sq]]
            atk[c][R] |= a
            atk2[c] |= atk[c][ALL] & a
            atk[c][ALL] |= a
            if a & their_ring:
                ka_count[c] += 1
                ka_weight[c] += KAW[R]
                ka_atk[c] += _popcount(a & KING_A[eks])
            mob = _popcount(a & m_area)
            if mob > MOB_MAX[2]: mob = MOB_MAX[2]
            mob_mg[c] += MOB_MG[2][mob]
            mob_eg[c] += MOB_EG[2][mob]
            fof = _SQ_FILE[sq]
            f_bb = FILE_BB[fof]
            if not (pp[P] & f_bb):
                if not (ppt[P] & f_bb):
                    piece_mg += sign * _ROF_MG
                    piece_eg += sign * _ROF_EG
                else:
                    piece_mg += sign * _RSF_MG
                    piece_eg += sign * _RSF_EG
            elif mob <= 3:
                kf = _SQ_FILE[ksq_us]
                if (kf < 4) == (fof < kf):
                    mult = 1 if board.castling & (1 if c==WHITE else 12) else 2
                    piece_mg -= sign * _TR_MG * mult
                    piece_eg -= sign * _TR_EG * mult
            if f_bb & (pp[Q] | ppt[Q]):
                piece_mg += sign * _RQF_MG
                piece_eg += sign * _RQF_EG
        bb = pp[Q]
        atk[c][Q] = 0
        while bb:
            lsb = bb & -bb
            sq = _LSB_TABLE[lsb]
            bb ^= lsb
            a = RT[sq][occ & RMK[sq]] | BT[sq][occ & BMK[sq]]
            atk[c][Q] |= a
            atk2[c] |= atk[c][ALL] & a
            atk[c][ALL] |= a
            if a & their_ring:
                ka_count[c] += 1
                ka_weight[c] += KAW[Q]
                ka_atk[c] += _popcount(a & KING_A[eks])
            mob = _popcount(a & m_area)
            if mob > MOB_MAX[3]: mob = MOB_MAX[3]
            mob_mg[c] += MOB_MG[3][mob]
            mob_eg[c] += MOB_EG[3][mob]
    mg_score += mob_mg[WHITE] - mob_mg[BLACK] + piece_mg
    eg_score += mob_eg[WHITE] - mob_eg[BLACK] + piece_eg
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        them = c ^ 1
        ksq = wksq if c == WHITE else bksq
        weak = atk[them][ALL] & ~atk2[c] & (~atk[c][ALL] | atk[c][K] | atk[c][Q])
        safe_sq = ~board.occ[them] & (~atk[c][ALL] | weak & atk2[them])
        cq = board.pieces[c][Q]
        b1 = RT[ksq][(occ ^ cq) & RMK[ksq]]
        b2 = BT[ksq][(occ ^ cq) & BMK[ksq]]
        king_danger = 0
        if b1 & safe_sq & atk[them][R]:
            king_danger += _ROOK_SAFE_CHECK
        qc = (b1|b2) & atk[them][Q] & safe_sq & ~atk[c][Q]
        if qc:
            king_danger += _QUEEN_SAFE_CHECK
        if b2 & atk[them][B] & safe_sq & ~qc:
            king_danger += _BISHOP_SAFE_CHECK
        if _KA[ksq] & atk[them][N] & safe_sq:
            king_danger += _KNIGHT_SAFE_CHECK
        king_ring_here = w_king_ring if c == WHITE else b_king_ring
        king_danger += (ka_count[them]*ka_weight[them] + 185*_popcount(king_ring_here&weak)
                        + 69*ka_atk[them] - 873*(1 if not board.pieces[them][Q] else 0)
                        - 100*bool(atk[c][N]&atk[c][K]) - 6*mob_mg[c]//8 + 37)
        if king_danger > 100:
            mg_score -= sign * (king_danger * king_danger // 4096)
            eg_score -= sign * (king_danger // 16)
        kf = ksq & 7
        if not (wp|bp) & KING_FLANK[kf]:
            mg_score -= sign * _PLF_MG
            eg_score -= sign * _PLF_EG
        camp = FULL_BOARD ^ (RANK_6|RANK_7|RANK_8) if c == WHITE else FULL_BOARD ^ (RANK_1|RANK_2|RANK_3)
        b1_fa = atk[them][ALL] & KING_FLANK[kf] & camp
        flank_atk = _popcount(b1_fa) + _popcount(b1_fa & atk2[them])
        mg_score -= sign * _FA_MG * flank_atk
        if board.pieces[them][Q]:
            krank = _SQ_RANK[ksq]
            kfile = _SQ_FILE[ksq]
            if 2 <= kfile <= 5:
                mg_score -= sign * 20 * ((krank if c==WHITE else 7-krank) + 1)
            if krank != (0 if c==WHITE else 7) and 2 <= kfile <= 5:
                mg_score -= sign * 50
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        passed_bb = w_passed if c == WHITE else b_passed
        ksq_us = wksq if c == WHITE else bksq
        ksq_them = bksq if c == WHITE else wksq
        DIST_ksqt = _DIST[ksq_them]
        DIST_ksqu = _DIST[ksq_us]
        tmp = passed_bb
        while tmp:
            lsb = tmp & -tmp
            sq = _LSB_TABLE[lsb]
            tmp ^= lsb
            rk = sq>>3 if c == WHITE else 7-(sq>>3)
            bmg = _PR_MG[rk]; beg = _PR_EG[rk]
            if rk > 2:
                w2 = 5*rk-13
                block_sq = sq+8 if c == WHITE else sq-8
                d_them = DIST_ksqt[block_sq]
                d_us = DIST_ksqu[block_sq]
                if d_them > 5: d_them = 5
                if d_us > 5: d_us = 5
                beg += (d_them*19//4 - d_us*2) * w2
                if rk != 6:
                    next_sq = block_sq+8 if c == WHITE else block_sq-8
                    if 0 <= next_sq < 64:
                        d2 = DIST_ksqu[next_sq]
                        if d2 > 5: d2 = 5
                        beg -= d2 * w2
                if not (occ & _SQ_BB[block_sq]):
                    fwd = 0
                    bb_tmp = _SQ_BB[block_sq]
                    for _ in range(6):
                        bb_tmp = (bb_tmp<<8)&FULL_BOARD if c==WHITE else bb_tmp>>8
                        fwd |= bb_tmp
                    unsafe = fwd & atk[them][ALL]
                    block_attacked = bool(atk[them][ALL] & _SQ_BB[block_sq])
                    k = 0 if block_attacked else (9 if unsafe else 20)
                    if atk[c][ALL] & _SQ_BB[block_sq] or board.occ[c] & fwd: k += 5
                    bmg += k*w2
                    beg += k*w2
            sq8 = sq+8 if c == WHITE else sq-8
            if 0 <= sq8 < 64 and occ & _SQ_BB[sq8]:
                bmg //= 2; beg //= 2
            f = sq & 7
            bmg -= _PFP_MG * _QUEENSIDE_MAP[f]
            beg -= _PFP_EG * _QUEENSIDE_MAP[f]
            mg_score += sign * bmg
            eg_score += sign * beg
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        seventh = RANK_7 if c == WHITE else RANK_2
        enemy_back = RANK_8 if c == WHITE else RANK_1
        rooks = board.pieces[c][R]
        on7 = rooks & seventh
        if on7:
            n = _popcount(on7)
            mg_score += sign * _R7_MG * n
            eg_score += sign * _R7_EG * n
            ek_sq = bksq if c == WHITE else wksq
            if 1<<ek_sq & enemy_back:
                mg_score += sign * _R7_MG * n
                eg_score += sign * _R7_EG * n
        if _popcount(rooks) >= 2:
            bb = rooks
            sqs = []
            while bb:
                lsb = bb & -bb
                sqs.append(_LSB_TABLE[lsb])
                bb ^= lsb
            for i in range(len(sqs)):
                for j in range(i+1, len(sqs)):
                    a2, b2 = sqs[i], sqs[j]
                    if (a2 & 7) == (b2 & 7) or (a2>>3) == (b2>>3):
                        mg_score += sign * _RB_MG
                        eg_score += sign * _RB_EG
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
            b_minor = (defended|weak) & (atk[c][N]|atk[c][B])
            while b_minor:
                lsb = b_minor & -b_minor
                sq = _LSB_TABLE[lsb]
                b_minor ^= lsb
                pc_there = board.piece_at[sq]
                if 0 <= pc_there <= 5:
                    mg_score += sign * _TBM_MG[pc_there]
                    eg_score += sign * _TBM_EG[pc_there]
            b_rook = weak & atk[c][R]
            while b_rook:
                lsb = b_rook & -b_rook
                sq = _LSB_TABLE[lsb]
                b_rook ^= lsb
                pc_there = board.piece_at[sq]
                if 0 <= pc_there <= 5:
                    mg_score += sign * _TBR_MG[pc_there]
                    eg_score += sign * _TBR_EG[pc_there]
            if weak & atk[c][K]:
                mg_score += sign * _TBK_MG
                eg_score += sign * _TBK_EG
            unattacked = ~atk[them][ALL] | non_pawn_enemies & atk2[c]
            n_hang = _popcount(weak & unattacked)
            mg_score += sign * _HNG_MG * n_hang
            eg_score += sign * _HNG_EG * n_hang
        safe_us = ~atk[them][ALL] | atk[c][ALL]
        sp_atk = _pawn_attacks_white(pp_us[P]&safe_us) if c==WHITE else _pawn_attacks_black(pp_us[P]&safe_us)
        n_spt = _popcount(sp_atk & non_pawn_enemies)
        mg_score += sign * _TBSP_MG * n_spt
        eg_score += sign * _TBSP_EG * n_spt
        if c == WHITE:
            push = pp_us[P] << 8 & ~occ & FULL_BOARD
            push2 = (push & RANK_3) << 8 & ~occ & FULL_BOARD
            push_atk = _pawn_attacks_white(push | push2)
        else:
            push = pp_us[P] >> 8 & ~occ
            push2 = (push & RANK_6) >> 8 & ~occ
            push_atk = _pawn_attacks_black(push | push2)
        push_atk &= ~atk[them][P] & safe_us
        mg_score += sign * _TBPP_MG * _popcount(push_atk & non_pawn_enemies)
        eg_score += sign * _TBPP_EG * _popcount(push_atk & non_pawn_enemies)
    npm = _non_pawn_material(board)
    if npm >= _SPACE_THRESHOLD:
        for c in (WHITE, BLACK):
            sign = 1 if c == WHITE else -1
            them = c ^ 1
            pp_us = board.pieces[c]
            space_mask = _SPACE_MASK_W if c==WHITE else _SPACE_MASK_B
            epa = b_pawn_atk if c==WHITE else w_pawn_atk
            safe = space_mask & ~pp_us[P] & ~epa
            behind = pp_us[P]
            if c == WHITE:
                behind |= behind>>8
                behind |= behind>>16
            else:
                behind = (behind | (behind<<8)&FULL_BOARD)
                behind = (behind | (behind<<16)&FULL_BOARD)
            bonus = _popcount(safe) + _popcount(behind & safe & ~atk[them][ALL])
            weight = _popcount(board.occ[c]) - 1
            if weight > 8: weight = 8
            space_score = bonus * weight * weight // 16
            if space_score > 40: space_score = 40
            mg_score += sign * space_score
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        knights = board.pieces[c][N]
        them_pawns = board.pieces[c^1][P]
        op_ranks = _OUTPOST_RANKS[c]
        while knights:
            lsb = knights & -knights
            sq = _LSB_TABLE[lsb]
            knights ^= lsb
            if not (1<<sq) & op_ranks: continue
            if PAWN_ATTACKS[c][sq] & them_pawns: continue
            f = sq & 7
            adj = (FILE_BB[f-1] if f>0 else 0) | (FILE_BB[f+1] if f<7 else 0)
            if not them_pawns & adj:
                mg_score += sign * _NOP_MG
                eg_score += sign * _NOP_EG
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        on_ctr = _popcount((board.pieces[c][N]|board.pieces[c][B]) & CENTER_4SQ)
        atk_ctr = _popcount((atk[c][N]|atk[c][B]) & CENTER_4SQ)
        mg_score += sign * _CCM_MG * (on_ctr*2 + atk_ctr)
        eg_score += sign * _CCM_EG * (on_ctr*2 + atk_ctr)
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        ksq = wksq if c == WHITE else bksq
        kf = ksq & 7
        if kf not in (0,1,6,7): continue
        flank = KING_FLANK[kf]
        own_p = board.pieces[c][P]
        them_p = board.pieces[c^1][P]
        for delta in ((8,16) if c==WHITE else (-8,-16)):
            sq2 = ksq + delta
            if 0 <= sq2 < 64 and (1<<sq2) & own_p & flank:
                mg_score += sign * _KSH_MG
        storm_zone = flank & (RANK_5|RANK_4|RANK_3) if c==WHITE else flank & (RANK_4|RANK_5|RANK_6)
        mg_score -= sign * _PS_MG * _popcount(them_p & storm_zone)
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        them = c ^ 1
        n_q = _popcount(board.pieces[c][Q])
        n_r = _popcount(board.pieces[c][R])
        n_b = _popcount(board.pieces[c][B])
        n_n = _popcount(board.pieces[c][N])
        if not (n_q or n_r or n_b or n_n): continue
        own_npm = n_n*300 + n_b*300 + n_r*500 + n_q*900 + _popcount(board.pieces[c][P])*100
        them_npm = (_popcount(board.pieces[them][N])*300 + _popcount(board.pieces[them][B])*300 +
                    _popcount(board.pieces[them][R])*500 + _popcount(board.pieces[them][Q])*900 +
                    _popcount(board.pieces[them][P])*100)
        advantage = own_npm - them_npm
        if advantage < 150: continue
        scale = min(256, (advantage-150)*256//250)
        ek_sq = bksq if c==WHITE else wksq
        ok_sq = wksq if c==WHITE else bksq
        k_dist = _DIST[ok_sq][ek_sq]
        only_bishops = n_b >= 2 and not n_q and not n_r
        pst_bonus = (_ENEMY_KING_CORNER_PST[ek_sq] * _MOPUP_CORNER_SCALE if only_bishops
                     else _ENEMY_KING_EDGE_PST[ek_sq] * _MOPUP_EDGE_SCALE)
        eg_score += sign * (pst_bonus + _MOPUP_PROXIMITY_BONUS * (14 - k_dist)) * scale // 256
    _UPP_VAL = (0, 300, 310, 500, 950, 99999)
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        them = c ^ 1
        for pc in (N, B, R, Q):
            bb = board.pieces[c][pc]
            while bb:
                lsb = bb & -bb
                sq = _LSB_TABLE[lsb]
                bb ^= lsb
                sq_bb = _SQ_BB[sq]
                if not (atk[them][ALL] & sq_bb): continue
                cheapest = 99999
                for apc in (P,N,B,R,Q,K):
                    if atk[them][apc] & sq_bb:
                        cheapest = _UPP_VAL[apc]
                        break
                if cheapest < _UPP_VAL[pc]:
                    penalty = (_UPP_VAL[pc] - cheapest) // 3
                    mg_score -= sign * penalty
                    eg_score -= sign * penalty
    if phase < 6:
        for c in (WHITE, BLACK):
            sign = 1 if c == WHITE else -1
            passed_bb = w_passed if c==WHITE else b_passed
            if not passed_bb: continue
            ek_sq = bksq if c==WHITE else wksq
            DIST_ek = _DIST[ek_sq]
            tmp = passed_bb
            while tmp:
                lsb = tmp & -tmp
                sq = _LSB_TABLE[lsb]
                tmp ^= lsb
                pawn_rank = sq >> 3
                promo_sq = (sq & 7) + (56 if c==WHITE else 0)
                pawn_dist = 7 - pawn_rank if c==WHITE else pawn_rank
                king_dist = DIST_ek[promo_sq]
                pawn_dist = max(1, pawn_dist if board.turn == c else pawn_dist + 1)
                if king_dist > pawn_dist:
                    eg_score += sign * 200
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        passed_bb = w_passed if c == WHITE else b_passed
        tmp = passed_bb
        rooks_c = board.pieces[c][R]
        while tmp:
            lsb = tmp & -tmp
            sq = _LSB_TABLE[lsb]
            tmp ^= lsb
            f = sq & 7
            f_bb = FILE_BB[f]
            rk = sq >> 3
            behind_bb = (f_bb & _BELOW_RANK[rk]) if c == WHITE else (f_bb & _ABOVE_RANK[rk])
            if rooks_c & behind_bb:
                mg_score += sign * _ROOK_BEHIND_PASSED_MG
                eg_score += sign * _ROOK_BEHIND_PASSED_EG
            front_bb = (f_bb & _ABOVE_RANK[rk]) if c == WHITE else (f_bb & _BELOW_RANK[rk])
            if rooks_c & front_bb:
                mg_score += sign * (_ROOK_BEHIND_PASSED_MG // 4)
                eg_score += sign * (_ROOK_BEHIND_PASSED_EG // 4)
    if phase < 10:
        for c in (WHITE, BLACK):
            sign = 1 if c == WHITE else -1
            ksq = wksq if c == WHITE else bksq
            kr = ksq >> 3; kf = ksq & 7
            centre_dist = max(abs(kf - 3), abs(kf - 4), abs(kr - 3), abs(kr - 4))
            eg_score += sign * _KING_CENTRAL_EG * (3 - centre_dist)
    if phase < 8:
        DIST_L = _DIST
        for c in (WHITE, BLACK):
            sign = 1 if c == WHITE else -1
            them = c ^ 1
            ksq_c = wksq if c == WHITE else bksq
            enemy_pieces = board.occ[them] & ~board.pieces[them][K]
            if not enemy_pieces:
                continue
            total_d = 0; n_ep = 0
            bb_ep = enemy_pieces
            dist_row = DIST_L[ksq_c]
            while bb_ep:
                lsb = bb_ep & -bb_ep
                sq_ep = _LSB_TABLE[lsb]
                bb_ep ^= lsb
                total_d += dist_row[sq_ep]
                n_ep += 1
            avg_d = total_d // n_ep
            eg_score += sign * _TROPISM_EG * (7 - avg_d)
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        them = c ^ 1
        if board.pieces[c][B] and not board.pieces[c][N] and board.pieces[them][N] and not board.pieces[them][B]:
            open_files = 0
            for fi in range(8):
                if not (wp | bp) & FILE_BB[fi]:
                    open_files += 1
            if open_files >= 3:
                mg_score += sign * _BISHOP_OPEN_MG * (open_files - 2)
                eg_score += sign * _BISHOP_OPEN_EG * (open_files - 2)
    for c in (WHITE, BLACK):
        sign = 1 if c == WHITE else -1
        them = c ^ 1
        xocc = occ ^ board.occ[c]
        rooks = board.pieces[c][R]
        while rooks:
            lsb = rooks & -rooks
            sq = _LSB_TABLE[lsb]
            rooks ^= lsb
            extra = RT[sq][xocc & RMK[sq]] & board.pieces[them][Q]
            if extra:
                n = _popcount(extra)
                mg_score += sign * _XR_MG * n
                eg_score += sign * _XR_EG * n
        bishops = board.pieces[c][B]
        while bishops:
            lsb = bishops & -bishops
            sq = _LSB_TABLE[lsb]
            bishops ^= lsb
            extra = BT[sq][xocc & BMK[sq]] & board.pieces[them][Q]
            if extra:
                n = _popcount(extra)
                mg_score += sign * _XR_MG * n
                eg_score += sign * _XR_EG * n
    outflanking = abs((wksq & 7) - (bksq & 7)) - abs((wksq>>3) - (bksq>>3))
    infiltration = (wksq>>3) > 3 or (bksq>>3) < 4
    pawns_both_flanks = bool((wp|bp) & QUEEN_SIDE) and bool((wp|bp) & KING_SIDE)
    n_passed = _popcount(w_passed) + _popcount(b_passed)
    n_pawns = _popcount(wp) + _popcount(bp)
    complexity = 9*n_passed + 11*n_pawns + 9*outflanking + 12*int(infiltration) + 21*int(pawns_both_flanks) - 100
    u = ((mg_score>0) - (mg_score<0)) * max(min(complexity+50, 0), -abs(mg_score))
    v = ((eg_score>0) - (eg_score<0)) * max(complexity, -abs(eg_score))
    mg_score += u
    eg_score += v
    kbnk = _is_kbnk(board)
    if kbnk is not None:
        winner_side, loser_side = kbnk
        raw = _eval_kbnk(board, winner_side, loser_side)
        result = raw if winner_side == WHITE else -raw
        return result if board.turn == WHITE else -result
    knnkp = _is_knnkp(board)
    if knnkp is not None:
        attacker, defender, pawn_sq = knnkp
        raw = _eval_knnkp(board, attacker, defender, pawn_sq)
        result = raw if attacker == WHITE else -raw
        return result if board.turn == WHITE else -result
    result = (mg_score * phase + eg_score * (PHASE_MAX - phase)) // PHASE_MAX
    result += _TEMPO * (8 + phase) // 16
    return result if board.turn == WHITE else -result
MG_VALUES = list(MAT_MG)
EG_VALUES = list(MAT_EG)
_W_MG = [list(t) for t in _RAW_MG_TABLES]
_B_MG = [list(t) for t in _RAW_MG_TABLES]
MG_TABLES = [_W_MG, _B_MG]
_W_EG = [list(t) for t in _RAW_EG_TABLES]
_B_EG = [list(t) for t in _RAW_EG_TABLES]
EG_TABLES = [_W_EG, _B_EG]
