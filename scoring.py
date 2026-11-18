# scoring.py
#
# Kowsar's task: a simple point system so solving a puzzle feels more
# rewarding than just a checkmark. Fewer attempts and fewer hints used
# means more points.

def calculate_points(attempt, hint_count):
    """
    Returns how many points a correctly solved puzzle is worth.

    - 100 points if solved on the first attempt
    - 50 points if solved on the second attempt
    - 25 points if solved on the third attempt
    - 0 points base for anything after that
    - Minus 10 points per hint used
    - Never goes below 0
    """
    if attempt == 1:
        points = 100
    elif attempt == 2:
        points = 50
    elif attempt == 3:
        points = 25
    else:
        points = 0

    points = points - (hint_count * 10)

    return max(0, points)

if __name__ == "__main__":
    print(calculate_points(1, 0))  # 100 -- first try, no hints
    print(calculate_points(2, 1))  # 40  -- second try, one hint
    print(calculate_points(3, 2))  # 5   -- third try, two hints
    print(calculate_points(1, 2))  # 80  -- first try, but used both hints