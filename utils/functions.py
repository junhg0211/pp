def center(screen, objet):
    return (screen - objet) / 2


def limit(value: int, m: int, x: int) -> int:
    return min(max(value, m), x)
