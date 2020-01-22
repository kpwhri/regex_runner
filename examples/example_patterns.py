from runrex.algo.pattern import Pattern

BURDEN = Pattern('(burden|debt)',
                 negates=['not?'],  # exclude a match
                 requires=['heavy', r'a\W*lot', 'significant']  # require this for match
                 )
