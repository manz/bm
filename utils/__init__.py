def xba(current_byte: list[int]) -> None:
    t = current_byte[0]
    current_byte[0] = current_byte[1]
    current_byte[1] = t
