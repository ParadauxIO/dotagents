def format_cents(cents):
    return f"${cents // 100}.{cents % 100:02d}"


def total_cents(prices, tax_percent=None):
    rate = tax_percent or 20
    subtotal = sum(prices)
    return subtotal + subtotal * rate // 100
