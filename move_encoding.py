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