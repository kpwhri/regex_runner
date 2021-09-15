"""
Useful phrases for negation when building patterns.
"""
from runrex.algo import Pattern

# date pattern
years_ago = r'(?:\d+ (?:year|yr|week|wk|month|mon|day)s? (?:ago|before|previous))'
date_pat = r'\d+[-/]\d+[-/]\d+'
date2_pat = r'\d+[/]\d+'
month_pat = r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sept|oct|nov|dec)\w*(?:\W*\d{1,2})?\W*\d{4}'
month_only_pat = r'in\b(?:jan|feb|mar|apr|may|jun|jul|aug|sept|oct|nov|dec)\w*'
DATE_PAT = Pattern(f'({years_ago}|{date_pat}|{date2_pat}|{month_pat}|{month_only_pat})')

# avoid 'last' or 'in' or 'since'
safe_may = r'(?<!in|st|ce) may (?!\d)'

# useful starting phrases for detecting negation, etc.
boilerplate = r'\b(pamphlet|warning|information|review|side effect|counsel|\bsign|ensure' \
              r'|risk|\bif\b|after your visit|appt|appointment|due (to|for|at)|recommend' \
              r'|pamphlet|schedul|doctor|contact|\bhow\b|\bcall|includ|failure|' \
              r'associated|avoid|instruct|guideline)'
possible = r'\b(unlikely|\bposs\b|possib(ly|le|ility)|improbable|potential|susp(ect|icious)|' \
           r'chance|may\b|afraid|concern|tentative|doubt|thought|think)'
POSSIBLE_PAT = Pattern(possible)

negation = r'(no evidence|without|r/o|rule out|normal|\bnot?\b|\bor\b|denies)'
historical = r'(history|previous|\bhx\b|\bpast\b|\bprior\b|\bh/o\b)'
hypothetical = r'(' \
               r'option|possib\w+|desire|want|will|\bcan\b|usual' \
               r'|\bor\b|like|would|need|until|request|when|you\Wll' \
               r'|\bif\b|consider|concern|return|nervous|anxious|could' \
               r'|discuss|inform|should|\btry|once|worr(y|ied)|question|ideal' \
               r')'
