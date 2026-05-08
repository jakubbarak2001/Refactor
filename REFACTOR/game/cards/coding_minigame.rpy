################################################################################
## REFACTOR — Coding Mini-Game (Phase 2)
##
## "Build the function" puzzle: spec at top, code blocks below (some correct,
## some distractors). Player clicks blocks in order to assemble the solution.
## Submit checks against the correct sequence. Pass = coding skill + card grant.
##
## Difficulty scales with: starting coding skill (we pick puzzle tier from skill).
## Retries scale with: difficulty (diff_setting("minigame_retries")).
################################################################################

init python:

    PUZZLES = {
        "p_easy_print": {
            "tier":   1,
            "spec":   "Write a function `greet()` that prints 'Hello, JB!'",
            "correct": [
                "def greet():",
                "    print(\"Hello, JB!\")",
            ],
            "distractors": [
                "return \"Hello, JB!\"",
                "print(\"Hello\", JB)",
                "def greet(JB):",
            ],
            "tests": ["greet() prints 'Hello, JB!'"],
            "reward_coding": 8,
        },

        "p_easy_double": {
            "tier":   1,
            "spec":   "Write a function `double(x)` that returns `x * 2`.",
            "correct": [
                "def double(x):",
                "    return x * 2",
            ],
            "distractors": [
                "    return x + x + 1",
                "    print(x * 2)",
                "def double(x, y):",
            ],
            "tests": ["double(3) -> 6", "double(7) -> 14"],
            "reward_coding": 8,
        },

        "p_medium_sum_even": {
            "tier":   2,
            "spec":   "Write a function `sum_even(numbers)` that returns the sum of even numbers in a list.",
            "correct": [
                "def sum_even(numbers):",
                "    total = 0",
                "    for n in numbers:",
                "        if n % 2 == 0:",
                "            total += n",
                "    return total",
            ],
            "distractors": [
                "    if n % 2 != 0:",
                "    return numbers",
                "    total = []",
                "    for n in total:",
            ],
            "tests": ["sum_even([1,2,3,4]) -> 6", "sum_even([2,4,6]) -> 12"],
            "reward_coding": 14,
        },

        "p_medium_max_in_list": {
            "tier":   2,
            "spec":   "Write a function `largest(items)` that returns the maximum value in a non-empty list, without using built-in `max()`.",
            "correct": [
                "def largest(items):",
                "    best = items[0]",
                "    for x in items[1:]:",
                "        if x > best:",
                "            best = x",
                "    return best",
            ],
            "distractors": [
                "    return max(items)",
                "    best = 0",
                "        if x < best:",
                "    return items[-1]",
            ],
            "tests": ["largest([3,1,4,1,5,9]) -> 9", "largest([-2,-7]) -> -2"],
            "reward_coding": 14,
        },

        "p_hard_fizzbuzz": {
            "tier":   3,
            "spec":   "Write `fizzbuzz(n)` that returns 'FizzBuzz' if divisible by 15, 'Fizz' by 3, 'Buzz' by 5, else str(n).",
            "correct": [
                "def fizzbuzz(n):",
                "    if n % 15 == 0:",
                "        return \"FizzBuzz\"",
                "    if n % 3 == 0:",
                "        return \"Fizz\"",
                "    if n % 5 == 0:",
                "        return \"Buzz\"",
                "    return str(n)",
            ],
            "distractors": [
                "    if n % 3 == 0 and n % 5 == 0:",
                "    return n",
                "    if n / 15:",
                "        print(\"FizzBuzz\")",
            ],
            "tests": ["fizzbuzz(15) -> 'FizzBuzz'", "fizzbuzz(9) -> 'Fizz'", "fizzbuzz(7) -> '7'"],
            "reward_coding": 22,
        },

        "p_hard_reverse": {
            "tier":   3,
            "spec":   "Write `reverse_words(s)` that reverses the order of words in a sentence (split on spaces).",
            "correct": [
                "def reverse_words(s):",
                "    parts = s.split(\" \")",
                "    parts.reverse()",
                "    return \" \".join(parts)",
            ],
            "distractors": [
                "    return s[::-1]",
                "    return s.reverse()",
                "    parts = s.split(\",\")",
            ],
            "tests": ["reverse_words('hello world') -> 'world hello'"],
            "reward_coding": 22,
        },
    }


    def pick_puzzle_for_skill(skill, exclude=None):
        """Pick a puzzle whose tier matches the player's current skill bracket.
        skill < 35: tier 1
        35-99:     tier 2
        100+:      tier 3
        """
        if skill < 35:
            tier = 1
        elif skill < 100:
            tier = 2
        else:
            tier = 3
        candidates = [pid for pid, p in PUZZLES.items() if p["tier"] == tier]
        if exclude:
            candidates = [c for c in candidates if c not in exclude]
        if not candidates:
            ## Fall back to any puzzle
            candidates = [pid for pid in PUZZLES.keys() if (not exclude or pid not in exclude)]
        return __import__('random').choice(candidates) if candidates else None


    ## Module-level state for the active puzzle interaction.
    puzzle_id        = None     ## current puzzle key
    puzzle_chosen    = []       ## list[block-text] in order
    puzzle_pool      = []       ## remaining (unselected) blocks, shuffled at start
    puzzle_attempts  = 0        ## attempts used
    puzzle_max_attempts = 1     ## set per call (difficulty: 1 + retries)
    puzzle_result    = None     ## "pass" / "fail" / None


    def puzzle_init(pid, max_attempts=1):
        """Set up an interactive puzzle. Resets state."""
        global puzzle_id, puzzle_chosen, puzzle_pool, puzzle_attempts, puzzle_max_attempts, puzzle_result
        puzzle_id = pid
        puzzle_chosen = []
        puzzle_attempts = 0
        puzzle_max_attempts = max_attempts
        puzzle_result = None
        p = PUZZLES.get(pid, {})
        pool = list(p.get("correct", [])) + list(p.get("distractors", []))
        __import__('random').shuffle(pool)
        puzzle_pool = pool


    def puzzle_pick_block(block_text):
        """Move a block from pool to chosen."""
        global puzzle_pool, puzzle_chosen
        if block_text in puzzle_pool:
            puzzle_pool.remove(block_text)
            puzzle_chosen.append(block_text)


    def puzzle_unpick_block(block_text):
        """Return a block from chosen to pool."""
        global puzzle_pool, puzzle_chosen
        if block_text in puzzle_chosen:
            puzzle_chosen.remove(block_text)
            puzzle_pool.append(block_text)


    def puzzle_reset():
        """Reset chosen back to pool."""
        global puzzle_pool, puzzle_chosen
        puzzle_pool = puzzle_pool + puzzle_chosen
        __import__('random').shuffle(puzzle_pool)
        puzzle_chosen = []


    def puzzle_submit():
        """Check chosen vs correct. Increments attempts. Sets puzzle_result.

        Returns None unconditionally — same Ren'Py-action-propagation
        hazard as battle_play_card: any non-None return from a Function
        action would short-circuit the screen, beating the timer-gated
        Return(puzzle_result) and mis-classifying even correct submissions
        as fail. The screen reads puzzle_result as a side-effect.
        """
        global puzzle_attempts, puzzle_result
        puzzle_attempts += 1
        p = PUZZLES.get(puzzle_id, {})
        correct = p.get("correct", [])
        if puzzle_chosen == correct:
            puzzle_result = "pass"
            return
        if puzzle_attempts >= puzzle_max_attempts:
            puzzle_result = "fail"
            return
        ## Reset for retry
        puzzle_reset()
