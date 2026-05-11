from constants import P, N, B, R, Q, K, WHITE, BLACK, BB_SQUARES, FULL_BOARD, NOT_FILE_A, NOT_FILE_H, RANK_1, RANK_2, RANK_3, RANK_6, RANK_7, RANK_8, KNIGHT_ATTACKS, KING_ATTACKS, PAWN_ATTACKS, RAYS, BETWEEN, LINE, CASTLE_WK, CASTLE_WQ, CASTLE_BK, CASTLE_BQ, CASTLE_EMPTY
from move_encoding import MT_QUIET, MT_DOUBLE_PUSH, MT_KING_CASTLE, MT_QUEEN_CASTLE, MT_CAPTURE, MT_EP_CAPTURE, MT_KNIGHT_PROMO, MT_BISHOP_PROMO, MT_ROOK_PROMO, MT_QUEEN_PROMO, MT_KNIGHT_PROMO_C, MT_BISHOP_PROMO_C, MT_ROOK_PROMO_C, MT_QUEEN_PROMO_C
_BL = int.bit_length
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
    checkers = _PA[us][king_sq] & pt[P] | _KA[king_sq] & pN
    if not (diag | orth):
        return checkers, 0
    pinned = 0
    _RN = _RAYS[0][king_sq]; _RE = _RAYS[2][king_sq]
    _RS = _RAYS[4][king_sq]; _RW = _RAYS[6][king_sq]
    _RNE = _RAYS[1][king_sq]; _RSE = _RAYS[3][king_sq]
    _RSW = _RAYS[5][king_sq]; _RNW = _RAYS[7][king_sq]
    if orth and _RN:
        bl = _RN & occ
        if bl:
            f = bl & -bl
            if f & orth: checkers |= f
            elif f & our_occ:
                be = _RN & ~((f << 1) - 1) & ~f & occ
                if be and be & -be & orth: pinned |= f
    if orth and _RE:
        bl = _RE & occ
        if bl:
            f = bl & -bl
            if f & orth: checkers |= f
            elif f & our_occ:
                be = _RE & ~((f << 1) - 1) & ~f & occ
                if be and be & -be & orth: pinned |= f
    if diag and _RNE:
        bl = _RNE & occ
        if bl:
            f = bl & -bl
            if f & diag: checkers |= f
            elif f & our_occ:
                be = _RNE & ~((f << 1) - 1) & ~f & occ
                if be and be & -be & diag: pinned |= f
    if diag and _RNW:
        bl = _RNW & occ
        if bl:
            f = bl & -bl
            if f & diag: checkers |= f
            elif f & our_occ:
                be = _RNW & ~((f << 1) - 1) & ~f & occ
                if be and be & -be & diag: pinned |= f
    if orth and _RS:
        bl = _RS & occ
        if bl:
            f = 1 << bl.bit_length() - 1
            if f & orth: checkers |= f
            elif f & our_occ:
                fs = f.bit_length() - 1
                bb2 = _RS & (1 << fs) - 1 & occ
                if bb2 and 1 << bb2.bit_length() - 1 & orth: pinned |= f
    if orth and _RW:
        bl = _RW & occ
        if bl:
            f = 1 << bl.bit_length() - 1
            if f & orth: checkers |= f
            elif f & our_occ:
                fs = f.bit_length() - 1
                bb2 = _RW & (1 << fs) - 1 & occ
                if bb2 and 1 << bb2.bit_length() - 1 & orth: pinned |= f
    if diag and _RSE:
        bl = _RSE & occ
        if bl:
            f = 1 << bl.bit_length() - 1
            if f & diag: checkers |= f
            elif f & our_occ:
                fs = f.bit_length() - 1
                bb2 = _RSE & (1 << fs) - 1 & occ
                if bb2 and 1 << bb2.bit_length() - 1 & diag: pinned |= f
    if diag and _RSW:
        bl = _RSW & occ
        if bl:
            f = 1 << bl.bit_length() - 1
            if f & diag: checkers |= f
            elif f & our_occ:
                fs = f.bit_length() - 1
                bb2 = _RSW & (1 << fs) - 1 & occ
                if bb2 and 1 << bb2.bit_length() - 1 & diag: pinned |= f
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
        to = _BL(lsb) - 1
        fr = to - fwd
        if BB[fr] & pinned and (not LINE[king_sq][fr] >> to & 1):
            continue
        ml.append(fr | to << 6 | _MT_Q | _P16)
    bb = double & check_mask
    while bb:
        lsb = bb & -bb
        bb ^= lsb
        to = _BL(lsb) - 1
        fr = to - fwd2
        if BB[fr] & pinned and (not LINE[king_sq][fr] >> to & 1):
            continue
        ml.append(fr | to << 6 | _MT_DP | _P16)
    bb = single & promo & check_mask
    while bb:
        lsb = bb & -bb
        bb ^= lsb
        to = _BL(lsb) - 1
        fr = to - fwd
        if BB[fr] & pinned and (not LINE[king_sq][fr] >> to & 1):
            continue
        base = fr | to << 6 | _P16
        ml.append(base | NKP)
        ml.append(base | BKP)
        ml.append(base | RKP)
        ml.append(base | QKP)
    bb = cl & check_mask
    while bb:
        lsb = bb & -bb
        bb ^= lsb
        to = _BL(lsb) - 1
        fr = to - cl_off
        if BB[fr] & pinned and (not LINE[king_sq][fr] >> to & 1):
            continue
        cap_pc = pat[to]
        if lsb & promo:
            base = fr | to << 6 | _P16 | cap_pc << 19
            ml.append(base | NKPC)
            ml.append(base | BKPC)
            ml.append(base | RKPC)
            ml.append(base | QKPC)
        else:
            ml.append(fr | to << 6 | _MT_CAP | _P16 | cap_pc << 19)
    bb = cr & check_mask
    while bb:
        lsb = bb & -bb
        bb ^= lsb
        to = _BL(lsb) - 1
        fr = to - cr_off
        if BB[fr] & pinned and (not LINE[king_sq][fr] >> to & 1):
            continue
        cap_pc = pat[to]
        if lsb & promo:
            base = fr | to << 6 | _P16 | cap_pc << 19
            ml.append(base | NKPC)
            ml.append(base | BKPC)
            ml.append(base | RKPC)
            ml.append(base | QKPC)
        else:
            ml.append(fr | to << 6 | _MT_CAP | _P16 | cap_pc << 19)
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
                to = _BL(lsb) - 1
                fr = to - off
                cap_sq = to - fwd
                occ2 = occ ^ BB2[fr] ^ BB2[cap_sq] | BB2[to]
                diag2 = pB_t | pQ_t
                if diag2 and BT[king_sq][occ2 & BMK[king_sq]] & diag2:
                    continue
                orth2 = pR_t | pQ_t
                if orth2 and RT[king_sq][occ2 & RMK[king_sq]] & orth2:
                    continue
                ml.append(fr | to << 6 | _MT_EP | _P16)
def _build_knight_quiet_moves():
    table = []
    N16 = N << 16
    MT_Q = MT_QUIET
    KA = KNIGHT_ATTACKS
    for fr in range(64):
        targets = KA[fr]
        moves = []
        bb = targets
        while bb:
            lsb = bb & -bb
            bb ^= lsb
            to = lsb.bit_length() - 1
            moves.append((lsb, fr | to << 6 | MT_Q | N16))
        table.append(moves)
    return table
_KNIGHT_QUIET_MOVES = _build_knight_quiet_moves()
def _gen_knight_moves(board, us, them, pinned, check_mask, ml):
    pu = board.pieces[us]
    knights = pu[N] & ~pinned
    if not knights:
        return
    tocc = board.occ[them]
    nocc = board.occ[us]
    pat = board.piece_at
    KA = _KA
    MT_CAP = _MT_CAP
    MT_Q = _MT_Q
    N16 = _N16
    while knights:
        lsb = knights & -knights
        knights ^= lsb
        fr = _BL(lsb) - 1
        targets = KA[fr] & ~nocc & check_mask
        caps = targets & tocc
        quiets = targets ^ caps
        while caps:
            alb = caps & -caps
            caps ^= alb
            to = _BL(alb) - 1
            ml.append(fr | to << 6 | MT_CAP | N16 | pat[to] << 19)
        while quiets:
            alb = quiets & -quiets
            quiets ^= alb
            ml.append(fr | (_BL(alb) - 1) << 6 | MT_Q | N16)
def _gen_bishop_moves(board, us, them, pinned, king_sq, check_mask, ml):
    pu = board.pieces[us]
    bishops = pu[B]
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
    while bishops:
        lsb = bishops & -bishops
        bishops ^= lsb
        fr = _BL(lsb) - 1
        attacks = BT[fr][occ & BMK[fr]] & ~nocc
        if lsb & pinned:
            attacks &= LINE[king_sq][fr]
        attacks &= check_mask
        caps = attacks & tocc
        quiets = attacks ^ caps
        while caps:
            alb = caps & -caps
            caps ^= alb
            to = _BL(alb) - 1
            ml.append(fr | to << 6 | MT_CAP | B16 | pat[to] << 19)
        while quiets:
            alb = quiets & -quiets
            quiets ^= alb
            ml.append(fr | (_BL(alb) - 1) << 6 | MT_Q | B16)
def _gen_rook_moves(board, us, them, pinned, king_sq, check_mask, ml):
    pu = board.pieces[us]
    rooks = pu[R]
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
    while rooks:
        lsb = rooks & -rooks
        rooks ^= lsb
        fr = _BL(lsb) - 1
        attacks = RT[fr][occ & RMK[fr]] & ~nocc
        if lsb & pinned:
            attacks &= LINE[king_sq][fr]
        attacks &= check_mask
        caps = attacks & tocc
        quiets = attacks ^ caps
        while caps:
            alb = caps & -caps
            caps ^= alb
            to = _BL(alb) - 1
            ml.append(fr | to << 6 | MT_CAP | R16 | pat[to] << 19)
        while quiets:
            alb = quiets & -quiets
            quiets ^= alb
            ml.append(fr | (_BL(alb) - 1) << 6 | MT_Q | R16)
def _gen_queen_moves(board, us, them, pinned, king_sq, check_mask, ml):
    pu = board.pieces[us]
    queens = pu[Q]
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
    while queens:
        lsb = queens & -queens
        queens ^= lsb
        fr = _BL(lsb) - 1
        attacks = (BT[fr][occ & BMK[fr]] | RT[fr][occ & RMK[fr]]) & ~nocc
        if lsb & pinned:
            attacks &= LINE[king_sq][fr]
        attacks &= check_mask
        caps = attacks & tocc
        quiets = attacks ^ caps
        while caps:
            alb = caps & -caps
            caps ^= alb
            to = _BL(alb) - 1
            ml.append(fr | to << 6 | MT_CAP | Q16 | pat[to] << 19)
        while quiets:
            alb = quiets & -quiets
            quiets ^= alb
            ml.append(fr | (_BL(alb) - 1) << 6 | MT_Q | Q16)
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
    while attacks:
        alb = attacks & -attacks
        attacks ^= alb
        to = _BL(alb) - 1
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
            ml.append(king_sq | to << 6 | MT_CAP | _K16 | pat[to] << 19)
        else:
            ml.append(king_sq | to << 6 | MT_Q | _K16)
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
                ml.append(king_sq | 6 << 6 | _MT_KC | _K16)
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
                ml.append(king_sq | 2 << 6 | _MT_QC | _K16)
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
                ml.append(king_sq | 62 << 6 | _MT_KC | _K16)
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
                ml.append(king_sq | 58 << 6 | _MT_QC | _K16)
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
    while attacks:
        alb = attacks & -attacks
        attacks ^= alb
        to = _BL(alb) - 1
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
        ml.append(king_sq | to << 6 | _MT_CAP | _K16 | pat[to] << 19)
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
        to = _BL(lsb) - 1
        fr = to - fwd
        if BB[fr] & pinned and (not LINE[king_sq][fr] >> to & 1):
            continue
        base = fr | to << 6 | _P16
        ml.append(base | NKP)
        ml.append(base | BKP)
        ml.append(base | RKP)
        ml.append(base | QKP)
    bb = cl & check_mask
    while bb:
        lsb = bb & -bb
        bb ^= lsb
        to = _BL(lsb) - 1
        fr = to - cl_off
        if BB[fr] & pinned and (not LINE[king_sq][fr] >> to & 1):
            continue
        cap_pc = pat[to]
        if lsb & promo:
            base = fr | to << 6 | _P16 | cap_pc << 19
            ml.append(base | NKPC)
            ml.append(base | BKPC)
            ml.append(base | RKPC)
            ml.append(base | QKPC)
        else:
            ml.append(fr | to << 6 | _MT_CAP | _P16 | cap_pc << 19)
    bb = cr & check_mask
    while bb:
        lsb = bb & -bb
        bb ^= lsb
        to = _BL(lsb) - 1
        fr = to - cr_off
        if BB[fr] & pinned and (not LINE[king_sq][fr] >> to & 1):
            continue
        cap_pc = pat[to]
        if lsb & promo:
            base = fr | to << 6 | _P16 | cap_pc << 19
            ml.append(base | NKPC)
            ml.append(base | BKPC)
            ml.append(base | RKPC)
            ml.append(base | QKPC)
        else:
            ml.append(fr | to << 6 | _MT_CAP | _P16 | cap_pc << 19)
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
                to = _BL(lsb) - 1
                fr = to - off
                cap_sq = to - fwd
                occ2 = occ ^ BB2[fr] ^ BB2[cap_sq] | BB2[to]
                diag2 = pB_t | pQ_t
                if diag2 and BT[king_sq][occ2 & BMK[king_sq]] & diag2:
                    continue
                orth2 = pR_t | pQ_t
                if orth2 and RT[king_sq][occ2 & RMK[king_sq]] & orth2:
                    continue
                ml.append(fr | to << 6 | _MT_EP | _P16)
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
        checker_sq = _BL(checkers) - 1
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
        return (ml, checkers, pinned, True)
    else:
        checker_sq = _BL(checkers) - 1
        check_mask = checkers | _BET[king_sq][checker_sq]
    _gen_king_moves(board, us, them, king_sq, check_mask, ml)
    _gen_pawn_moves(board, us, them, pinned, king_sq, check_mask, ml)
    _gen_knight_moves(board, us, them, pinned, check_mask, ml)
    _gen_bishop_moves(board, us, them, pinned, king_sq, check_mask, ml)
    _gen_rook_moves(board, us, them, pinned, king_sq, check_mask, ml)
    _gen_queen_moves(board, us, them, pinned, king_sq, check_mask, ml)
    return (ml, checkers, pinned, in_check)
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
        checker_sq = _BL(checkers) - 1
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
        checker_sq = _BL(checkers) - 1
        check_mask = checkers | _BET[king_sq][checker_sq]
    cap_mask = check_mask & board.occ[them]
    _gen_king_captures(board, us, them, king_sq, ml)
    _gen_pawn_captures(board, us, them, pinned, king_sq, check_mask, ml)
    _gen_knight_moves(board, us, them, pinned, cap_mask, ml)
    _gen_bishop_moves(board, us, them, pinned, king_sq, cap_mask, ml)
    _gen_rook_moves(board, us, them, pinned, king_sq, cap_mask, ml)
    _gen_queen_moves(board, us, them, pinned, king_sq, cap_mask, ml)
    return ml
