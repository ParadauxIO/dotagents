from billing import format_cents, total_cents


def receipt(prices, tax_percent=None):
    return "Total: " + format_cents(total_cents(prices, tax_percent))


def preview(prices, tax_percent=None):
    return {"amount_cents": total_cents(prices, tax_percent)}
