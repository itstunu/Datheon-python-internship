# portfolio.py
"""
Stock Portfolio Tracker - Datheon Python Internship, Task 2
===========================================================

Enter your stock positions (ticker, buy price, number of shares) and the
script computes invested amount, current value, gain/loss and percentage
return per holding, prints an aligned table, and exports a CSV summary.

Notes
-----
* Current prices come from the static MARKET_PRICES dictionary (sample
  data - no internet / API needed).
* A ticker that is not in MARKET_PRICES is shown with current price "N/A"
  and is valued at its invested amount (gain = 0).
* Output file: portfolio_summary.csv (written next to this script).

Usage
---
    python portfolio.py
    (type 'done' when you have entered all positions)
"""

import csv
import math
from pathlib import Path

# Sample market data (USD). Edit freely to experiment.
MARKET_PRICES = {
    "AAPL": 228.50,
    "MSFT": 415.20,
    "GOOGL": 178.30,
    "AMZN": 205.75,
    "TSLA": 245.60,
    "NVDA": 135.40,
    "META": 585.90,
    "NFLX": 890.25,
}

OUTPUT_FILE = Path(__file__).parent / "portfolio_summary.csv"
SEPARATOR = "=" * 50
MAX_NUMBER = 1e12  # sanity cap so absurd inputs cannot overflow the maths


def prompt_ticker(portfolio):
    """Ask for a ticker. Return it in uppercase, or None when user types 'done'."""
    while True:
        raw = input("Ticker (or 'done' to finish): ").strip()
        if raw.lower() == "done":
            return None
        ticker = raw.upper()
        if not ticker:
            print("❌ Ticker cannot be empty.")
        elif not (ticker.isascii() and ticker.isalpha()):
            print("❌ Ticker must contain letters only (e.g. AAPL).")
        elif ticker in portfolio:
            print(f"⚠ {ticker} is already in your portfolio - enter a different ticker.")
        else:
            return ticker


def prompt_positive_number(label):
    """Ask for a number > 0 (accepts '1,500.50'). Re-prompts until valid."""
    while True:
        raw = input(label).strip().replace(",", "")
        try:
            value = float(raw)
        except ValueError:
            print("❌ Please enter a valid number (e.g. 150.25).")
            continue
        # float() accepts 'nan' and 'inf', so reject those explicitly.
        if not math.isfinite(value):
            print("❌ Please enter a normal finite number.")
        elif value <= 0:
            print("❌ Value must be greater than 0.")
        elif value > MAX_NUMBER:
            print("❌ That number is unrealistically large.")
        else:
            return value


def collect_positions():
    """Interactive loop that builds {ticker: {"buy_price": f, "shares": f}}."""
    portfolio = {}
    print("Enter your positions below. Type 'done' as the ticker to finish.")
    print(f"Known tickers: {', '.join(MARKET_PRICES)}")
    print(SEPARATOR)
    try:
        while True:
            ticker = prompt_ticker(portfolio)
            if ticker is None:
                break
            if ticker not in MARKET_PRICES:
                print(f"⚠ No market price for {ticker}; it will be valued at cost (N/A).")
            buy_price = prompt_positive_number("  Buy price per share ($): ")
            shares = prompt_positive_number("  Number of shares:        ")
            portfolio[ticker] = {"buy_price": buy_price, "shares": shares}
            print(f"✔ Added {ticker}\n")
    except (KeyboardInterrupt, EOFError):
        # Not a crash: just stop collecting and use what we already have.
        print("\n⚠ Input interrupted - continuing with positions entered so far.")
    return portfolio


def analyse(portfolio):
    """Compute per-holding metrics and portfolio totals.

    Returns (rows, totals) where each row is a dict with:
    ticker, buy_price, shares, current, invested, value, gain, pct.
    """
    rows = []
    for ticker, pos in portfolio.items():
        invested = pos["buy_price"] * pos["shares"]
        current = MARKET_PRICES.get(ticker, "N/A")
        # Unknown ticker -> valued at cost, so gain is exactly 0.
        value = invested if current == "N/A" else current * pos["shares"]
        gain = value - invested
        rows.append({
            "ticker": ticker,
            "buy_price": pos["buy_price"],
            "shares": pos["shares"],
            "current": current,
            "invested": invested,
            "value": value,
            "gain": gain,
            "pct": gain / invested * 100,   # invested is always > 0
        })

    total_invested = sum(r["invested"] for r in rows)
    total_value = sum(r["value"] for r in rows)
    total_gain = total_value - total_invested
    totals = {
        "invested": total_invested,
        "value": total_value,
        "gain": total_gain,
        "pct": total_gain / total_invested * 100 if total_invested else 0.0,
    }
    return rows, totals


def fmt_shares(shares):
    """Show whole share counts without decimals, fractional ones trimmed."""
    if float(shares).is_integer():
        return f"{shares:,.0f}"
    return f"{shares:,.4f}".rstrip("0").rstrip(".")


def table_line(t, buy, shares, cur, inv, val, gain, pct):
    """One aligned table line (all arguments are pre-formatted strings)."""
    return (f"{t:<8} | {buy:>10} | {shares:>10} | {cur:>10} | "
            f"{inv:>12} | {val:>12} | {gain:>12} | {pct:>9}")


def print_table(rows, totals):
    """Print the formatted portfolio table followed by a TOTAL row."""
    header = table_line("TICKER", "BUY", "SHARES", "CURRENT",
                        "INVESTED", "VALUE", "GAIN", "%")
    rule = "=" * len(header)
    print(rule)
    print(header)
    print(rule)
    for r in rows:
        cur = "N/A" if r["current"] == "N/A" else f"{r['current']:,.2f}"
        print(table_line(
            r["ticker"], f"{r['buy_price']:,.2f}", fmt_shares(r["shares"]), cur,
            f"{r['invested']:,.2f}", f"{r['value']:,.2f}",
            f"{r['gain']:+,.2f}", f"{r['pct']:+.2f}%",
        ))
    print(rule)
    print(table_line(
        "TOTAL", "", "", "",
        f"{totals['invested']:,.2f}", f"{totals['value']:,.2f}",
        f"{totals['gain']:+,.2f}", f"{totals['pct']:+.2f}%",
    ))
    print(rule)


def export_csv(rows, totals, path=OUTPUT_FILE):
    """Write the summary CSV (UTF-8) including a TOTAL row. Return True on success."""
    try:
        # newline="" prevents blank lines between rows on Windows.
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["Ticker", "Buy Price", "Shares", "Current Price",
                             "Invested", "Current Value", "Gain/Loss", "Gain/Loss %"])
            for r in rows:
                cur = "N/A" if r["current"] == "N/A" else f"{r['current']:.2f}"
                writer.writerow([
                    r["ticker"], f"{r['buy_price']:.2f}", fmt_shares(r["shares"]).replace(",", ""),
                    cur, f"{r['invested']:.2f}", f"{r['value']:.2f}",
                    f"{r['gain']:.2f}", f"{r['pct']:.2f}",
                ])
            writer.writerow(["TOTAL", "", "", "", f"{totals['invested']:.2f}",
                             f"{totals['value']:.2f}", f"{totals['gain']:.2f}",
                             f"{totals['pct']:.2f}"])
        return True
    except OSError as exc:  # e.g. file open in Excel, read-only folder
        print(f"❌ Could not write CSV: {exc}")
        return False


def main():
    print(SEPARATOR)
    print("💹  STOCK PORTFOLIO TRACKER  -  Datheon Internship")
    print(SEPARATOR)

    portfolio = collect_positions()
    if not portfolio:
        print("\n⚠ No positions entered - nothing to calculate. Goodbye!")
        return

    rows, totals = analyse(portfolio)
    print(f"\n📊 PORTFOLIO SUMMARY ({len(rows)} holding{'s' if len(rows) != 1 else ''})")
    print_table(rows, totals)

    if totals["gain"] > 0:
        print(f"✔ Portfolio is UP {totals['pct']:+.2f}% ({totals['gain']:+,.2f} USD)")
    elif totals["gain"] < 0:
        print(f"❌ Portfolio is DOWN {totals['pct']:+.2f}% ({totals['gain']:+,.2f} USD)")
    else:
        print("⚠ Portfolio is flat (no gain or loss).")

    if export_csv(rows, totals):
        print(f"\n📄 CSV exported to: {OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
