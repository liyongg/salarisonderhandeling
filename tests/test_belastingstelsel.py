from utils.belastingstelsel import belastingstelsels


def test_structure():
    # Check that belastingstelsels is a dict with expected year keys.
    for year in belastingstelsels.keys():
        assert isinstance(year, int), (
            f"Jaar {year} moet een integer zijn, is {type(year)}"
        )
        categories = belastingstelsels[year]
        required_categories = ("arbeidskorting", "heffingskorting", "schijven")
        for cat in required_categories:
            assert cat in categories, f"Categorie '{cat}' ontbreekt in jaar {year}"
            tarieven = categories[cat]
            # Check that tarieven is a dict mapping tuple keys to callables.
            for interval, func in tarieven.items():
                assert isinstance(interval, tuple) and len(interval) == 2, (
                    f"Interval '{cat}' ({year}) moet van lengte 2 zijn)"
                )
                a, b = interval
                assert isinstance(a, (int, float)) and isinstance(b, (int, float)), (
                    "Interval bounds must be numeric"
                )
                assert callable(func), f"Waarde van '{cat}' ({year}) is geen callable"


def test_belastingstelsel_interval():
    # Check that all intervals in belastingstelsels have valid numeric boundaries.
    for year, categories in belastingstelsels.items():
        for cat, tarieven in categories.items():
            intervals = list(tarieven.keys())
            # First, check individual intervals.
            for interval in intervals:
                a, b = interval
                assert isinstance(a, (int, float)), (
                    f"Ondergrens van interval {interval} in {cat} ({year}) moet een getal zijn"
                )
                assert isinstance(b, (int, float)), (
                    f"Bovengrens van interval {interval} in {cat} ({year}) moet een getal zijn"
                )
                assert a < b, (
                    f"Ondergrens {a} moet kleiner zijn dan bovengrens {b} voor '{cat}' ({year})"
                )
            # Then, check that intervals are consecutive.
            for prev, curr in zip(intervals, intervals[1:]):
                prev_a, prev_b = prev
                curr_a, curr_b = curr
                assert prev_b == curr_a, (
                    f"De bovengrens {prev_b} van {prev} in '{cat}' ({year}) is ongelijk zijn aan "
                    f"de ondergrens {curr_a} van het volgende interval {curr}"
                )
