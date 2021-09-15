from runrex.algo import Pattern

BURDEN = Pattern('(burden|debt)',
                 negates=['not?'],  # exclude a match
                 requires=['heavy', r'a\W*lot', 'significant']  # require this for match
                 )
