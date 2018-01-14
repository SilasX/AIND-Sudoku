
from utils import *


row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [
    cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI')
    for cs in ('123', '456', '789')
]
unitlist = row_units + column_units + square_units

diag_units = [
    [rows[i] + cols[i] for i in range(len(rows))],
    [rows[len(rows) - 1 - i] + cols[i] for i in range(len(rows))],
]

unitlist = unitlist + diag_units

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], []))-set([s])) for s in boxes)


def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the naked twins eliminated from peers

    Notes
    -----
    Your solution can either process all pairs of naked twins from the input once,
    or it can continue processing pairs of naked twins until there are no such
    pairs remaining -- the project assistant test suite will accept either
    convention. However, it will not accept code that does not process all pairs
    of naked twins from the original input. (For example, if you start processing
    pairs of twins and eliminate another pair of twins before the second pair
    is processed then your code will fail the PA test suite.)

    The first convention is preferred for consistency with the other strategies,
    and because it is simpler (since the reduce_puzzle function already calls this
    strategy repeatedly).
    """
    # TODO: Implement this function!
    raise NotImplementedError


def eliminate(values):
    """Apply the eliminate strategy to a Sudoku puzzle

    The eliminate strategy says that if a box has a value assigned, then none
    of the peers of that box can have the same value.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the assigned values eliminated from peers
    """
    # Get all the solved boxes
    known_vals = [x for x in values if len(values[x]) == 1]
    # Remove those as a possibility from their peers
    for known_val in known_vals:
        for peer in peers[known_val]:
            values[peer] = values[peer].replace(values[known_val], "")
    return values


def only_choice(values):
    """Apply the only choice strategy to a Sudoku puzzle

    The only choice strategy says that if only one box in a unit allows a certain
    digit, then that box must be assigned that digit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with all single-valued boxes assigned

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    """
    for unit in unitlist:
        # For each option list in the unit, use `matches` to point each option
        # to the box that still has it as an option. If the element was
        # already in the list, this is a dupe and ignore it instead
        matches = {}
        dupes = set()
        for box in unit:
            if len(values[box]) == 1:
                dupes.add(values[box])
                continue
            for number in values[box]:
                if number in matches:
                    dupes.add(number)
                else:
                    matches[number] = box
        # anything left was the only option for that number
        for number, box in matches.items():
            if number in dupes:
                continue
            values[box] = number
    return values


def reduce_puzzle(values):
    """Reduce a Sudoku puzzle by repeatedly applying all constraint strategies

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary after continued application of the constraint strategies
        no longer produces any changes, or False if the puzzle is unsolvable 
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Reduce by use of Eliminate and Only Choice strategy
        values = eliminate(values)
        values = only_choice(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """Apply depth first search to solve Sudoku puzzles in order to solve puzzles
    that cannot be solved by repeated reduction alone.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary with all boxes assigned or False

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    and extending it to call the naked twins strategy.
    """
    # values_mod is a copy of values so the originals are unaffected
    values_mod = dict(values)
    values_mod = reduce_puzzle(values_mod)
    if values_mod is False:
        # Discovered it's not a valid solution, skip out here
        return False
    # Get the list of boxes with more than one possibility
    unsolved = [box for box in values_mod if len(values_mod[box]) > 1]
    # If there are none, this is the solution; return it.
    if len(unsolved) == 0:
        return values_mod

    # Otherwise take a/the box with the minimum number of possibilities
    min_pos_box = min(
        unsolved,
        key=lambda x: len(values_mod[x])
    )
    # For each possibility in that min box,
    # recurse. Return the first non-false answer
    for possible_value in values_mod[min_pos_box]:
        candidate_solution = dict(values_mod)
        candidate_solution[min_pos_box] = possible_value
        candidate_solution = search(candidate_solution)
        if not (candidate_solution is False):
            return candidate_solution
    # If none returned, all came back false, so the whole branch is bad.
    return False


def solve(grid):
    """Find the solution to a Sudoku puzzle using search and constraint propagation

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.
        
        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    Returns
    -------
    dict or False
        The dictionary representation of the final sudoku grid or False if no solution exists.
    """
    values = grid2values(grid)
    values = search(values)
    return values


if __name__ == "__main__":
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(grid2values(diag_sudoku_grid))
    result = solve(diag_sudoku_grid)
    display(result)

    try:
        import PySudoku
        PySudoku.play(grid2values(diag_sudoku_grid), result, history)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
