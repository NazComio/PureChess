import time, random
from moves import generate_legal_moves, generate_legal_moves_ex, generate_captures, generate_captures_from_info, _BISHOP_TABLE, _BISHOP_MASKS, _ROOK_TABLE, _ROOK_MASKS
from move_encoding import FLAG_PROMO, FLAG_CAPTURE, promo_piece
from evaluation import MG_VALUES, MG_TABLES, EG_TABLES, FLIP, evaluate
from constants import P, N, B, R, Q, K, WHITE, BLACK, PAWN_ATTACKS, BB_SQUARES, KNIGHT_ATTACKS, KING_ATTACKS, CASTLE_WK, CASTLE_WQ, CASTLE_BK, CASTLE_BQ, CASTLE_RIGHTS_MASK, CASTLE_ROOK_FROM, CASTLE_ROOK_TO
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
