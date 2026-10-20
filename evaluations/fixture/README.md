# Receipt utility

This local Python utility handles nonnegative integer prices in cents and integer
tax percentages. `None` selects the default 20% tax. Round fractional tax cents
down. There are no external dependencies or services. Run checks with
`python3 -m unittest discover -s tests -v`.
