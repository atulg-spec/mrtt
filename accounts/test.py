def get_level(members: int) -> int:
    """
    Given members count, return the corresponding level.
    Uses the 'Total Members Required' sequence.
    """
    level = 1
    total_required = 2  # level 1 total

    while total_required <= members:
        level += 1
        total_required = (2 ** (level + 1)) - 2  # formula for total members required
    
    return level - 1

print(get_level(2))