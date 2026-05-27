import time, random
from moves import generate_legal_moves, generate_legal_moves_ex, generate_captures, generate_captures_from_info, get_attack_info, _BISHOP_TABLE, _BISHOP_MASKS, _ROOK_TABLE, _ROOK_MASKS
from move_encoding import FLAG_PROMO, FLAG_CAPTURE, promo_piece
from nnue_eval import _IB as _NNUE_IB, _OW as _NNUE_OW, _OB as _NNUE_OB, _SCALE as _NNUE_SCALE, _FW as _NNUE_FW, _N_HIDDEN as _NNUE_N_HIDDEN
from constants import P, N, B, R, Q, K, WHITE, BLACK, PAWN_ATTACKS, BB_SQUARES, KNIGHT_ATTACKS, KING_ATTACKS, CASTLE_WK, CASTLE_WQ, CASTLE_BK, CASTLE_BQ, CASTLE_RIGHTS_MASK, CASTLE_ROOK_FROM, CASTLE_ROOK_TO
MATE_SCORE = 100000
INF = MATE_SCORE + 1
MAX_DEPTH = 64
import array as _array
_TT_SIZE: int = 0
_TT_MASK: int = 0
_TT_H: _array.array = _array.array('Q')
_TT_D: _array.array = _array.array('b')
_TT_F: _array.array = _array.array('b')
_TT_S: _array.array = _array.array('i')
_TT_M: _array.array = _array.array('i')
def resize_tt(mb: int) -> None:
    global _TT_SIZE, _TT_MASK, _TT_H, _TT_D, _TT_F, _TT_S, _TT_M
    mb   = max(1, int(mb))
    raw  = (mb * 1024 * 1024) // 18
    size = 1
    while size * 2 <= raw:
        size *= 2
    _TT_SIZE = size
    _TT_MASK = size - 1
    _TT_H = _array.array('Q', bytes(size * _array.array('Q').itemsize))
    _TT_D = _array.array('b', bytes(size * _array.array('b').itemsize))
    _TT_F = _array.array('b', bytes(size * _array.array('b').itemsize))
    _TT_S = _array.array('i', bytes(size * _array.array('i').itemsize))
    _TT_M = _array.array('i', bytes(size * _array.array('i').itemsize))
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
_LMR_TABLE = [[0] * 64 for _ in range(64)]
for _sd in range(64):
    for _mi in range(64):
        if _mi >= LMR_MIN_M and _sd >= LMR_MIN_D:
            _LMR_TABLE[_sd][_mi] = max(1, int((_sd ** 0.5 + (_mi - LMR_MIN_M) ** 0.5) * 0.45 + 0.5))
del _sd, _mi
_H = _NNUE_N_HIDDEN
_AF = _array.array('f', [0.0] * (768 * _H))
for _fi, _col in enumerate(_NNUE_FW):
    _base_fi = _fi * _H
    for _hi, _v in enumerate(_col):
        _AF[_base_fi + _hi] = _v
_IB_ARR = _array.array('f', _NNUE_IB)
_OW_SC = _array.array('f', (w * _NNUE_SCALE for w in _NNUE_OW))
_OB_SC = float(_NNUE_OB * _NNUE_SCALE)
_QD: dict = {}
for _color in range(2):
    for _pc in range(6):
        _base_c = _color * 384 + _pc * 64
        for _fr in range(64):
            _ff = _base_c + _fr
            _ff_base = _ff * _H
            for _to in range(64):
                if _fr == _to:
                    continue
                _tf = _base_c + _to
                _tf_base = _tf * _H
                _d = _array.array('f', (
                    _AF[_tf_base + _i] - _AF[_ff_base + _i]
                    for _i in range(_H)
                ))
                _QD[_ff * 768 + _tf] = _d
del _color, _pc, _base_c, _fr, _ff, _ff_base, _to, _tf, _tf_base, _d, _fi, _col, _base_fi, _hi, _v
_SNAP_POOL = [_array.array('f', [0.0] * _H) for _ in range(MAX_DEPTH + 10)]
def _acc_add(acc: _array.array, feat: int) -> None:
    base = feat * _H
    af   = _AF
    for i in range(_H):
        acc[i] += af[base + i]
def _acc_sub(acc: _array.array, feat: int) -> None:
    base = feat * _H
    af   = _AF
    for i in range(_H):
        acc[i] -= af[base + i]
def _acc_add_delta(acc: _array.array, key: int) -> None:
    d = _QD[key]
    for i in range(_H):
        acc[i] += d[i]
def _full_score(board) -> _array.array:
    acc = _array.array('f', _IB_ARR)
    pcs = board.pieces
    af  = _AF
    h   = _H
    for color in (WHITE, BLACK):
        base = color * 384
        for pc in range(6):
            base_pc = base + pc * 64
            bb = pcs[color][pc]
            while bb:
                feat = base_pc + (bb & -bb).bit_length() - 1
                fb   = feat * h
                for i in range(h):
                    acc[i] += af[fb + i]
                bb &= bb - 1
    return acc
def _nnue_output(acc: _array.array) -> int:
    ow  = _OW_SC
    out = _OB_SC
    for i in range(_H):
        v = acc[i]
        if   v < 0.0: v = 0.0
        elif v > 1.0: v = 1.0
        out += v * ow[i]
    return int(out)
def _fast_eval(acc: _array.array, turn) -> int:
    cp = _nnue_output(acc)
    return cp if turn == WHITE else -cp
def _acc_push(acc: _array.array, stack: list) -> None:
    buf = _SNAP_POOL[len(stack)]
    buf[:] = acc
    stack.append(buf)
def _acc_pop(acc: _array.array, stack: list) -> None:
    acc[:] = stack.pop()
def _score_delta(board, move: int, acc: _array.array, acc_stack: list) -> None:
    _acc_push(acc, acc_stack)
    us   = board.turn
    them = us ^ 1
    fr   = move & 63
    to   = move >> 6 & 63
    pc   = move >> 16 & 7
    mt   = move >> 12 & 15
    us6  = us   * 384
    th6  = them * 384
    QD   = _QD
    if mt >= 8:
        pp = promo_piece(move)
        _acc_add(acc, us6 + pp * 64 + to)
        _acc_sub(acc, us6 + P  * 64 + fr)
        if mt >= 12:
            cap = move >> 19 & 7
            if cap <= 5:
                _acc_sub(acc, th6 + cap * 64 + to)
    elif mt == 5:
        cap_sq = board.ep_sq + (-8 if us == WHITE else 8)
        ff = us6 + P * 64 + fr
        tf = us6 + P * 64 + to
        _acc_add_delta(acc, ff * 768 + tf)
        _acc_sub(acc, th6 + P * 64 + cap_sq)
    elif mt == 2 or mt == 3:
        flag = (CASTLE_WK if us == WHITE else CASTLE_BK) if mt == 2 \
               else (CASTLE_WQ if us == WHITE else CASTLE_BQ)
        rf = CASTLE_ROOK_FROM[flag]; rt = CASTLE_ROOK_TO[flag]
        fk  = us6 + K * 64 + fr;  tk  = us6 + K * 64 + to
        fr_ = us6 + R * 64 + rf;  tr_ = us6 + R * 64 + rt
        _acc_add_delta(acc, fk  * 768 + tk)
        _acc_add_delta(acc, fr_ * 768 + tr_)
    elif move & FLAG_CAPTURE:
        cap = move >> 19 & 7
        ff = us6 + pc * 64 + fr; tf = us6 + pc * 64 + to
        _acc_add_delta(acc, ff * 768 + tf)
        if cap <= 5:
            _acc_sub(acc, th6 + cap * 64 + to)
    else:
        ff = us6 + pc * 64 + fr; tf = us6 + pc * 64 + to
        _acc_add_delta(acc, ff * 768 + tf)
def _nnue_eval_from_stack(score_stack, turn):
    cp = _nnue_output(score_stack[-1])
    return cp if turn == WHITE else -cp
_rng = random.Random(3735928559)
_ZP = [[_rng.getrandbits(64) for _ in range(64)] for _ in range(12)]
_ZT = _rng.getrandbits(64)
_ZC = [_rng.getrandbits(64) for _ in range(16)]
_ZE = [_rng.getrandbits(64) for _ in range(65)]
_ZP_FLAT = [_ZP[i][j] for i in range(12) for j in range(64)]
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
    zp = _ZP_FLAT
    h = old_h
    ze = _ZE
    ep64 = old_ep if old_ep != -1 else 64
    zpc_us_base = (pc + (0 if us == WHITE else 6)) * 64
    h ^= zp[zpc_us_base + fr] ^ zp[zpc_us_base + to]
    if mt == 1:
        h ^= ze[ep64] ^ ze[(fr + to) >> 1]
    elif mt == 5:
        h ^= zp[(P + (0 if them == WHITE else 6)) * 64 + old_ep + (-8 if us == WHITE else 8)]
        h ^= ze[ep64] ^ ze[64]
    elif mt == 2 or mt == 3:
        flag = (CASTLE_WK if us == WHITE else CASTLE_BK) if mt == 2 else \
               (CASTLE_WQ if us == WHITE else CASTLE_BQ)
        rf = CASTLE_ROOK_FROM[flag]
        rt = CASTLE_ROOK_TO[flag]
        zr_base = (R + (0 if us == WHITE else 6)) * 64
        h ^= zp[zr_base + rf] ^ zp[zr_base + rt]
        h ^= ze[ep64] ^ ze[64]
    elif mt >= 8:
        cap = move >> 19 & 7
        h ^= zp[zpc_us_base + to]
        h ^= zp[(promo_piece(move) + (0 if us == WHITE else 6)) * 64 + to]
        if mt >= 12 and cap <= 5:
            h ^= zp[(cap + (0 if them == WHITE else 6)) * 64 + to]
        h ^= ze[ep64] ^ ze[64]
    elif mt == 4:
        cap = move >> 19 & 7
        if cap <= 5:
            h ^= zp[(cap + (0 if them == WHITE else 6)) * 64 + to]
        h ^= ze[ep64] ^ ze[64]
    else:
        h ^= ze[ep64] ^ ze[64]
    new_cr = old_cr & CASTLE_RIGHTS_MASK[fr] & CASTLE_RIGHTS_MASK[to]
    if new_cr != old_cr:
        h ^= _ZC[old_cr & 15] ^ _ZC[new_cr & 15]
    return h ^ _ZT
def _tt_probe(h, depth, alpha, beta):
    idx = h & _TT_MASK
    if _TT_H[idx] != h:
        return (None, 0)
    em = _TT_M[idx]
    ed = _TT_D[idx]
    if ed >= depth:
        ef = _TT_F[idx]
        es = _TT_S[idx]
        if ef == TT_EXACT:
            return (es, em)
        if ef == TT_LOWER and es >= beta:
            return (es, em)
        if ef == TT_UPPER and es <= alpha:
            return (es, em)
    return (None, em)
def _tt_store(h, depth, flag, score, move):
    idx = h & _TT_MASK
    if _TT_H[idx] != h or _TT_D[idx] <= depth or (_TT_D[idx] == depth and flag == TT_EXACT and _TT_F[idx] != TT_EXACT):
        _TT_H[idx] = h & 0xFFFFFFFFFFFFFFFF
        _TT_D[idx] = depth
        _TT_F[idx] = flag
        _TT_S[idx] = score
        _TT_M[idx] = move
_SEE_PA = PAWN_ATTACKS
_SEE_KA = KNIGHT_ATTACKS
_SEE_KGA = KING_ATTACKS
_SEE_BB = BB_SQUARES
_SEE_BT = _BISHOP_TABLE
_SEE_BMK = _BISHOP_MASKS
_SEE_RT = _ROOK_TABLE
_SEE_RMK = _ROOK_MASKS
_SEE_V = _SEE_VAL
_SEE_GAIN_BUF = [0] * 32
_SEE_PCOPY_BUF = [0] * 12
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
    pc = _SEE_PCOPY_BUF
    pc[0] = p[0][0]; pc[1] = p[0][1]; pc[2] = p[0][2]
    pc[3] = p[0][3]; pc[4] = p[0][4]; pc[5] = p[0][5]
    pc[6] = p[1][0]; pc[7] = p[1][1]; pc[8] = p[1][2]
    pc[9] = p[1][3]; pc[10] = p[1][4]; pc[11] = p[1][5]
    pc[us * 6 + agg_pc] ^= _SEE_BB[fr]
    p_copy = pc
    gain = _SEE_GAIN_BUF
    gain[0] = gain0
    d = 0
    side = them
    BT = _SEE_BT; BMK = _SEE_BMK; RT = _SEE_RT; RMK = _SEE_RMK
    KA = _SEE_KA; KGA = _SEE_KGA; PA = _SEE_PA; SV = _SEE_V
    while True:
        d += 1
        gain[d] = SV[agg_pc] - gain[d - 1]
        if -gain[d - 1] < 0 and gain[d] < 0:
            break
        base = side * 6
        lva_bb = 0; agg_pc = -1
        att = PA[side ^ 1][to] & p_copy[base + P] & occ
        if att:
            lva_bb = att & -att; agg_pc = P
        else:
            att = KA[to] & p_copy[base + N] & occ
            if att:
                lva_bb = att & -att; agg_pc = N
            else:
                diag = BT[to][occ & BMK[to]]
                att = diag & p_copy[base + B] & occ
                if att:
                    lva_bb = att & -att; agg_pc = B
                else:
                    orth = RT[to][occ & RMK[to]]
                    att = orth & p_copy[base + R] & occ
                    if att:
                        lva_bb = att & -att; agg_pc = R
                    else:
                        att = (diag | orth) & p_copy[base + Q] & occ
                        if att:
                            lva_bb = att & -att; agg_pc = Q
                        else:
                            att = KGA[to] & p_copy[base + K] & occ
                            if att:
                                lva_bb = att & -att; agg_pc = K
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
    pw = board.pieces[WHITE]; pb = board.pieces[BLACK]
    if pw[P] | pb[P] | pw[R] | pb[R] | pw[Q] | pb[Q]:
        return False
    wm = (pw[N] | pw[B]).bit_count()
    bm = (pb[N] | pb[B]).bit_count()
    total = wm + bm
    if total <= 1:
        return True
    if wm == 1 and bm == 1 and pw[N] == 0 and pb[N] == 0:
        _DARK = 12273903644374837845
        if bool(pw[B] & _DARK) == bool(pb[B] & _DARK):
            return True
    return False
def _pawnless_scale(board) -> int:
    if board.pieces[WHITE][P] | board.pieces[BLACK][P]:
        return 1
    pw = board.pieces[WHITE]; pb = board.pieces[BLACK]
    if pw[R] | pw[Q] | pb[R] | pb[Q]:
        return 1
    w_n = pw[N].bit_count(); w_b = pw[B].bit_count()
    b_n = pb[N].bit_count(); b_b = pb[B].bit_count()
    wm = w_n + w_b; bm = b_n + b_b
    if wm >= 2 and bm == 0:
        return 4 if w_n == 2 and w_b == 0 else 1
    if bm >= 2 and wm == 0:
        return 4 if b_n == 2 and b_b == 0 else 1
    return 2 if wm + bm <= 2 else 1
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
_MAT_APPROX = (82, 337, 365, 477, 1025, 20000, 0)
def _make_cont_hist():
    return [[[0] * 64 for _ in range(6)] for _ in range(384)]
_MM = 15 << 12
_KC_M = 2 << 12
_QC_M = 3 << 12
_EP_M = 5 << 12
_DBL_M = 1 << 12
_FILTER_OFFSET = 20000000
_FILTER_MMASK = 0xFFFFFFFF
def _filter_and_score(raw_moves, board, k1, k2, hist, cont_hist, prev_pc: int, prev_to: int, cap_hist, counter_move: int, tt_move: int=0):
    FC = FLAG_CAPTURE; FP = FLAG_PROMO
    PB = _PROMO_BONUS; SGB = _SEE_GOOD_BASE; SBB = _SEE_BAD_BASE
    PA = _PA_LOCAL; turn = board.turn; _OFF = _FILTER_OFFSET
    packed = []; append = packed.append
    ch_row = cont_hist[prev_pc * 64 + prev_to] if prev_pc >= 0 else None
    cap_h = cap_hist[turn]
    pcs_enemy_P = board.pieces[turn ^ 1][0]
    for m in raw_moves:
        mt = m & _MM
        if mt == _KC_M or mt == _QC_M:
            sc = 10000000 if m == tt_move else 0
            append((sc + _OFF) << 32 | m); continue
        if m == tt_move:
            sc = 10000000
        elif m & FP:
            bonus = PB[m >> 12 & 3]
            if m & FC:
                vv = m >> 19 & 7
                if vv <= 5: bonus += _MV_LOCAL[vv]
            sc = 90000 + bonus
        elif m & FC:
            atk = m >> 16 & 7; vic = m >> 19 & 7
            ch_bonus = cap_h[atk][vic] if vic <= 5 else 0
            ma_vic = _MAT_APPROX[vic]; ma_atk = _MAT_APPROX[atk]
            if ma_vic > ma_atk:
                sc = SGB + ma_vic - ma_atk + ch_bonus // 4
            elif ma_vic == ma_atk:
                sc = SGB + ch_bonus // 4
            else:
                see_val = see(board, m)
                sc = (SGB + see_val + ch_bonus // 4) if see_val >= 0 else (SBB + see_val)
        else:
            pc = m >> 16 & 7; to = m >> 6 & 63
            h_val = hist[pc][to]
            ch_val = ch_row[pc][to] if ch_row is not None else 0
            base = h_val + ch_val
            if pc and PA[turn ^ 1][to] & pcs_enemy_P:
                base -= 50
            if m == k1:       sc = 70000
            elif m == k2:     sc = 69000
            elif m == counter_move: sc = 68000
            else:             sc = base
        append((sc + _OFF) << 32 | m)
    packed.sort(reverse=True)
    _M = _FILTER_MMASK
    return [p & _M for p in packed]
class Searcher:
    __slots__ = ('nodes', '_start_time', '_end_time', '_stop', '_killers1', '_killers2',
                 '_hist', '_cont_hist', '_cap_hist', '_counter_moves', '_acc', '_acc_stack',
                 '_rep_counts', '_best_move_changes')
    def __init__(self):
        self.nodes = 0
        self._start_time = 0.0; self._end_time = 0.0; self._stop = False
        self._killers1 = [0] * (MAX_DEPTH + 10)
        self._killers2 = [0] * (MAX_DEPTH + 10)
        self._hist = [[[0] * 64 for _ in range(6)] for _ in range(2)]
        self._cont_hist = _make_cont_hist()
        self._cap_hist = [[[0] * 6 for _ in range(6)] for _ in range(2)]
        self._counter_moves = [[0] * 64 for _ in range(64)]
        self._acc = _array.array('f', _IB_ARR)
        self._acc_stack = []
        self._rep_counts = {}
        self._best_move_changes = 0
    def _check_time(self):
        if not self._stop and self.nodes & 1023 == 0:
            if time.time() >= self._end_time:
                self._stop = True
    def _build_history_counts(self, board):
        self._rep_counts.clear()
        if not board._undo:
            self._rep_counts[_full_hash(board)] = 1
            return
        moves_made = []
        while board._undo:
            moves_made.append(board._undo[-1][0])
            board.unmake_move(board._undo[-1][0])
        h = _full_hash(board)
        self._rep_counts[h] = self._rep_counts.get(h, 0) + 1
        for move in reversed(moves_made):
            board.make_move(move)
            h = _full_hash(board)
            self._rep_counts[h] = self._rep_counts.get(h, 0) + 1
    def _quiesce(self, board, alpha: int, beta: int, h: int, checkers: int=-1, pinned: int=-1) -> int:
        self.nodes += 1
        if self.nodes & 1023 == 0 and not self._stop:
            if time.time() >= self._end_time:
                self._stop = True
        if self._stop:
            return 0
        rep = self._rep_counts
        if rep.get(h, 0) >= 2:
            return 0
        if board.phase_total == 0 and _is_material_draw(board):
            return 0
        _, tt_move = _tt_probe(h, 0, alpha, beta)
        sp = _fast_eval(self._acc, board.turn)
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
            FP = FLAG_PROMO; FC = FLAG_CAPTURE; PB = _PROMO_BONUS
            mv = _MV_LOCAL; cap_h = self._cap_hist[board.turn]
            _OFF = 10001000; packed = []; _MA = _MAT_APPROX
            pack_append = packed.append
            for m in captures:
                if m == tt_move:
                    pack_append((_OFF + 10000000) << 32 | m); continue
                if m & FP:
                    bonus = PB[m >> 12 & 3]
                    if m & FC:
                        v = m >> 19 & 7
                        if v <= 5: bonus += mv[v]
                    pack_append((_OFF + 90000 + bonus) << 32 | m)
                elif m & FC:
                    atk = m >> 16 & 7; vic = m >> 19 & 7
                    ch_b = cap_h[atk][vic] if vic <= 5 else 0
                    if _MA[vic] > _MA[atk]:
                        pack_append((_OFF + _MA[vic] - _MA[atk] + ch_b // 8) << 32 | m)
                    else:
                        see_val = see(board, m)
                        if not in_check and see_val < 0: continue
                        pack_append((_OFF + see_val + ch_b // 8) << 32 | m)
                else:
                    pack_append(_OFF << 32 | m)
            if not packed:
                return alpha
            packed.sort(reverse=True)
            _MMASK = 0xFFFFFFFF
            captures = [p & _MMASK for p in packed]
        else:
            m = captures[0]
            if m & FLAG_CAPTURE and (not in_check) and (not m & FLAG_PROMO):
                if see(board, m) < 0:
                    return alpha
        SV = _SEE_VAL
        acc = self._acc; acc_stack = self._acc_stack
        _sd = _score_delta; _ap = _acc_pop; _dh = _delta_hash
        _mm = board.make_move; _um = board.unmake_move
        for move in captures:
            if not in_check and move & FLAG_CAPTURE and (not move & FLAG_PROMO):
                cap_pc = move >> 19 & 7
                if cap_pc <= 5 and sp + SV[cap_pc] + 200 < alpha:
                    continue
            new_h = _dh(board, move, h)
            rep[new_h] = rep.get(new_h, 0) + 1
            _sd(board, move, acc, acc_stack)
            _mm(move)
            score = -self._quiesce(board, -beta, -alpha, new_h)
            _um(move)
            _ap(acc, acc_stack)
            cnt = rep[new_h] - 1
            if cnt <= 0: del rep[new_h]
            else:        rep[new_h] = cnt
            if self._stop:
                return 0
            if score >= beta:
                if move & FLAG_CAPTURE and (not move & FLAG_PROMO):
                    atk = move >> 16 & 7; vic = move >> 19 & 7
                    if vic <= 5:
                        ch = self._cap_hist[board.turn ^ 1]
                        ch[atk][vic] = min(ch[atk][vic] + 1, 30000)
                return beta
            if score > alpha:
                alpha = score
        return alpha
    def _negamax(self, board, depth: int, alpha: int, beta: int, ply: int, h: int, null_ok: bool, prev_fr: int=-1, prev_pc: int=-1, prev_to: int=0, is_singular: bool=False) -> int:
        self.nodes += 1
        if self.nodes & 1023 == 0 and not self._stop:
            if time.time() >= self._end_time:
                self._stop = True
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
        if board.phase_total == 0 and _is_material_draw(board):
            return 0
        tt_score, tt_move = _tt_probe(h, depth, alpha, beta)
        if tt_score is not None and (not is_singular):
            return tt_score
        if depth <= 0:
            score = self._quiesce(board, alpha, beta, h)
            if not (board.pieces[WHITE][P] | board.pieces[BLACK][P] |
                    board.pieces[WHITE][R] | board.pieces[BLACK][R] |
                    board.pieces[WHITE][Q] | board.pieces[BLACK][Q]):
                sc = _pawnless_scale(board)
                if sc > 1:
                    score = score // sc
            return score
        us = board.turn
        raw_moves, checkers, pinned_mask, in_check = generate_legal_moves_ex(board)
        hm = board.halfmove
        if hm >= 100 and not in_check:
            return 0
        static_eval = _fast_eval(self._acc, us) if not in_check else 0
        if not in_check and depth <= RAZOR_DEPTH and (abs(alpha) < MATE_SCORE - 100):
            se = static_eval
            if hm >= 80: se = se * (100 - hm) // 20
            if se + RAZOR_MARGIN[depth] < alpha:
                qsc = self._quiesce(board, alpha, beta, h)
                if qsc < alpha:
                    return qsc
        if not in_check and depth <= RFP_MAX_D and (abs(beta) < MATE_SCORE - 100):
            se = static_eval
            if hm >= 80: se = se * (100 - hm) // 20
            if se - RFP_MARGIN * depth >= beta:
                return beta
        if not in_check and depth >= PROBCUT_MIN_D and (abs(beta) < MATE_SCORE - 100):
            se = static_eval
            pc_beta = beta + PROBCUT_BETA
            see_threshold = pc_beta - se
            acc = self._acc; acc_stack = self._acc_stack
            for pc_move in raw_moves:
                if not pc_move & FLAG_CAPTURE: continue
                if pc_move & FLAG_PROMO: continue
                if see(board, pc_move) < see_threshold: continue
                new_h = _delta_hash(board, pc_move, h)
                rep[new_h] = rep.get(new_h, 0) + 1
                _score_delta(board, pc_move, acc, acc_stack)
                board.make_move(pc_move)
                pc_pc = pc_move >> 16 & 7; pc_to = pc_move >> 6 & 63
                pc_sc = -self._negamax(board, depth - 4, -pc_beta, -pc_beta + 1, ply + 1, new_h, False, pc_move & 63, pc_pc, pc_to)
                board.unmake_move(pc_move)
                _acc_pop(acc, acc_stack)
                cnt = rep[new_h] - 1
                if cnt <= 0: del rep[new_h]
                else:        rep[new_h] = cnt
                if self._stop: return 0
                if pc_sc >= pc_beta:
                    _tt_store(h, depth - 3, TT_LOWER, pc_sc, pc_move)
                    return pc_beta
        if null_ok and (not in_check) and depth >= NMP_MIN_D:
            se = static_eval
            if se >= beta and (board.pieces[us][Q] | board.pieces[us][R] | board.pieces[us][B] | board.pieces[us][N]):
                nmp_red = NMP_BASE_R + depth // 6 + min(3, (se - beta) // 200)
                nmp_red = min(nmp_red, NMP_MAX_R, depth - 1)
                old_ep = board.ep_sq
                board.turn ^= 1
                board.ep_sq = -1
                nh = h ^ _ZT ^ _ZE[old_ep if old_ep != -1 else 64] ^ _ZE[64]
                rep[nh] = rep.get(nh, 0) + 1
                acc = self._acc; acc_stack = self._acc_stack
                _acc_push(acc, acc_stack)
                sc = -self._negamax(board, depth - 1 - nmp_red, -beta, -beta + 1, ply + 1, nh, False)
                _acc_pop(acc, acc_stack)
                board.turn ^= 1; board.ep_sq = old_ep
                cnt = rep[nh] - 1
                if cnt <= 0: del rep[nh]
                else:        rep[nh] = cnt
                if self._stop: return 0
                if sc >= beta:
                    _tt_store(h, depth, TT_LOWER, beta, 0)
                    return beta
        eff_depth = depth
        if depth >= IIR_MIN_D and tt_move == 0 and (not in_check):
            eff_depth = depth - 1
        counter_move = self._counter_moves[prev_fr][prev_to] if prev_fr >= 0 else 0
        k1 = self._killers1[ply]; k2 = self._killers2[ply]
        hist = self._hist[us]
        ch = self._cont_hist
        cap_hist = self._cap_hist
        if not raw_moves:
            moves = raw_moves
        elif len(raw_moves) == 1:
            moves = raw_moves
        else:
            moves = _filter_and_score(raw_moves, board, k1, k2, hist, ch, prev_pc, prev_to, cap_hist, counter_move, tt_move)
        if not moves:
            return -(MATE_SCORE - ply) if in_check else 0
        orig_alpha = alpha
        best_move = moves[0]; best_score = -INF
        do_futility = not in_check and eff_depth <= FP_DEPTH and (abs(alpha) < MATE_SCORE - 100)
        fut_threshold = (static_eval + FP_MARGIN[eff_depth]) if do_futility else 0
        lmp_limit = LMP_BASE + eff_depth * eff_depth if not in_check and eff_depth < LMP_MAX_D else 9999
        quiet_count = 0
        acc = self._acc; acc_stack = self._acc_stack
        _sd = _score_delta; _ap = _acc_pop; _dh = _delta_hash
        _mm = board.make_move; _um = board.unmake_move
        lmr = _LMR_TABLE
        for i, move in enumerate(moves):
            is_cap = bool(move & FLAG_CAPTURE)
            is_pro = bool(move & FLAG_PROMO)
            pc = move >> 16 & 7; to = move >> 6 & 63; fr = move & 63
            if not is_cap and not is_pro:
                quiet_count += 1
            if not is_cap and not is_pro and quiet_count > lmp_limit and i > 0 and hist[pc][to] <= 0:
                continue
            if do_futility and not is_cap and not is_pro and fut_threshold < alpha and i > 0:
                continue
            if not in_check and is_cap and not is_pro and eff_depth <= SEE_PRUNE_D and i > 0:
                if see(board, move) < -50 * eff_depth:
                    continue
            extension = 0
            if eff_depth >= SE_MIN_D and move == tt_move and not is_singular and tt_move != 0 and abs(tt_score if tt_score is not None else 0) < MATE_SCORE - 100:
                se_beta = max(alpha, (tt_score if tt_score is not None else static_eval) - SE_MARGIN)
                se_depth = eff_depth - 3 | 1
                se_score = self._negamax(board, se_depth, se_beta - 1, se_beta, ply, h, False, prev_fr, prev_pc, prev_to, is_singular=True)
                if self._stop: return 0
                if se_score < se_beta: extension = 1
            elif prev_to >= 0 and is_cap and to == prev_to:
                extension = 1
            new_h = _dh(board, move, h)
            rep[new_h] = rep.get(new_h, 0) + 1
            _sd(board, move, acc, acc_stack)
            _mm(move)
            if not extension and eff_depth <= 4:
                new_us = board.turn
                new_ksq = (board.pieces[new_us][5] & -board.pieces[new_us][5]).bit_length() - 1
                if new_ksq >= 0:
                    if pc == 1:
                        if KNIGHT_ATTACKS[to] >> new_ksq & 1: extension = 1
                    elif pc == 0:
                        if PAWN_ATTACKS[us][to] >> new_ksq & 1: extension = 1
            search_depth = eff_depth - 1 + extension
            if i >= LMR_MIN_M and search_depth >= LMR_MIN_D and not is_cap and not is_pro and not in_check:
                red = lmr[min(search_depth, 63)][min(i, 63)]
                if red == 0: red = 1
                if move == k1 or move == k2 or move == counter_move:
                    red = max(1, red - 1)
                elif hist[pc][to] < -2000:
                    red += 1
                elif pc == N:
                    enemy_heavy = board.pieces[us ^ 1][R] | board.pieces[us ^ 1][Q]
                    if KNIGHT_ATTACKS[to] & enemy_heavy: red = max(1, red - 1)
                elif pc == B:
                    enemy_heavy = board.pieces[us ^ 1][R] | board.pieces[us ^ 1][Q]
                    if _BISHOP_TABLE[to][board.all_occ & _BISHOP_MASKS[to]] & enemy_heavy: red = max(1, red - 1)
                red = min(red, search_depth - 1)
                score = -self._negamax(board, search_depth - red, -alpha - 1, -alpha, ply + 1, new_h, True, fr, pc, to)
                if self._stop:
                    _um(move); _ap(acc, acc_stack)
                    cnt = rep[new_h] - 1
                    if cnt <= 0: del rep[new_h]
                    else:        rep[new_h] = cnt
                    return 0
                if score > alpha:
                    score = -self._negamax(board, search_depth, -beta, -alpha, ply + 1, new_h, True, fr, pc, to)
            elif i > 0:
                score = -self._negamax(board, search_depth, -alpha - 1, -alpha, ply + 1, new_h, True, fr, pc, to)
                if self._stop:
                    _um(move); _ap(acc, acc_stack)
                    cnt = rep[new_h] - 1
                    if cnt <= 0: del rep[new_h]
                    else:        rep[new_h] = cnt
                    return 0
                if score > alpha:
                    score = -self._negamax(board, search_depth, -beta, -alpha, ply + 1, new_h, True, fr, pc, to)
            else:
                score = -self._negamax(board, search_depth, -beta, -alpha, ply + 1, new_h, True, fr, pc, to)
            _um(move); _ap(acc, acc_stack)
            cnt = rep[new_h] - 1
            if cnt <= 0: del rep[new_h]
            else:        rep[new_h] = cnt
            if self._stop: return 0
            if score > best_score:
                best_score = score; best_move = move
            if score > alpha:
                alpha = score
            if score >= beta:
                if not is_cap and not is_pro:
                    self._killers2[ply] = self._killers1[ply]
                    self._killers1[ply] = move
                    if prev_fr >= 0:
                        self._counter_moves[prev_fr][prev_to] = move
                    bonus = eff_depth * eff_depth
                    h_tbl = hist
                    h_tbl[pc][to] += bonus
                    for j in range(i):
                        prev_m = moves[j]
                        if not prev_m & FLAG_CAPTURE and not prev_m & FLAG_PROMO:
                            h_tbl[prev_m >> 16 & 7][prev_m >> 6 & 63] -= bonus
                    if h_tbl[pc][to] > 60000:
                        for pp in range(6):
                            row = h_tbl[pp]
                            for sq in range(64): row[sq] >>= 1
                    if prev_pc >= 0:
                        idx = prev_pc * 64 + prev_to
                        v = ch[idx][pc][to] + bonus
                        ch[idx][pc][to] = v if v < 30000 else 30000
                else:
                    atk = move >> 16 & 7; vic = move >> 19 & 7
                    if vic <= 5:
                        cap_h2 = self._cap_hist[us]
                        cap_h2[atk][vic] = min(cap_h2[atk][vic] + eff_depth, 30000)
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
        self.nodes = 0; self._best_move_changes = 0
        self._killers1 = [0] * (MAX_DEPTH + 10)
        self._killers2 = [0] * (MAX_DEPTH + 10)
        self._hist = [[[0] * 64 for _ in range(6)] for _ in range(2)]
        self._acc = _full_score(board)
        self._acc_stack = []
        self._build_history_counts(board)
        if _is_material_draw(board):
            return (None, 0)
        raw_root = generate_legal_moves(board)
        k1 = self._killers1[0]; k2 = self._killers2[0]
        hist = self._hist[board.turn]
        ch = self._cont_hist; cap_hist = self._cap_hist
        root_moves = _filter_and_score(raw_root, board, k1, k2, hist, ch, -1, 0, cap_hist, 0)
        if not root_moves:
            return (None, 0)
        root_h = _full_hash(board)
        best_move = root_moves[0]
        best_score = _fast_eval(self._acc, board.turn)
        prev_best = best_move
        for depth in range(1, MAX_DEPTH + 1):
            if self._stop: break
            aw_lo = best_score - ASPIRATION if depth >= 2 else -INF
            aw_hi = best_score + ASPIRATION if depth >= 2 else INF
            aw_width = ASPIRATION
            depth_best_move = best_move; depth_best_score = -INF
            while True:
                if self._stop: break
                alpha = aw_lo; depth_best_score = -INF; depth_best_move = best_move
                k1 = self._killers1[0]; k2 = self._killers2[0]
                _, ttm = _tt_probe(root_h, depth, aw_lo, aw_hi)
                root_moves = _filter_and_score(root_moves, board, k1, k2, hist, ch, -1, 0, cap_hist, 0, ttm)
                rep = self._rep_counts
                acc = self._acc; acc_stack = self._acc_stack
                for move in root_moves:
                    if self._stop: break
                    self.nodes += 1
                    new_h = _delta_hash(board, move, root_h)
                    rep[new_h] = rep.get(new_h, 0) + 1
                    _score_delta(board, move, acc, acc_stack)
                    pc = move >> 16 & 7; to = move >> 6 & 63; fr = move & 63
                    board.make_move(move)
                    score = -self._negamax(board, depth - 1, -aw_hi, -alpha, 1, new_h, True, fr, pc, to)
                    board.unmake_move(move)
                    _acc_pop(acc, acc_stack)
                    cnt = rep[new_h] - 1
                    if cnt <= 0: del rep[new_h]
                    else:        rep[new_h] = cnt
                    if self._stop: break
                    if score > depth_best_score:
                        depth_best_score = score; depth_best_move = move
                    if score > alpha: alpha = score
                if self._stop: break
                if depth >= 2:
                    if depth_best_score <= aw_lo:
                        aw_width *= 4; aw_lo = max(-INF, depth_best_score - aw_width)
                    elif depth_best_score >= aw_hi:
                        aw_width *= 4; aw_hi = min(INF, depth_best_score + aw_width)
                    else:
                        break
                    if aw_lo <= -INF + 1 and aw_hi >= INF - 1: break
                else:
                    break
            if not self._stop:
                best_move = depth_best_move; best_score = depth_best_score
                if best_move != prev_best:
                    self._best_move_changes += 1; prev_best = best_move
            if self._end_time - time.time() <= 0:
                break
        return (best_move, best_score)
