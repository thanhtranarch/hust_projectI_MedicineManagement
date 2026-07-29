"""
Reusable SQL fragments.

SQLite has no date subtraction operator, so "how many days until this date"
needs a julianday() expression that is too noisy to repeat inside queries.
"""

# Today's date, in the machine's local timezone
TODAY = "date('now','localtime')"


def days_until(column):
    """
    SQL expression for the whole days from today until a timestamp column.

    Negative for dates already in the past.
    """
    return f"CAST(julianday(date({column})) - julianday({TODAY}) AS INTEGER)"
