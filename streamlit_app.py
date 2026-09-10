import streamlit as st

st.title("Test App Loading...")


import finnhub

# Initialize Finnhub Client with your API Key
FINNHUB_API_KEY = "dagv8qpr01qomffm2jl0dagv8qpr01qomffm2jlg"
finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)


class PortfolioGameManager:

    def __init__(self, initial_cash=100000.0):
        self.cash = initial_cash
        self.portfolio = {
            "STOCK": {},  # {ticker: {"shares": qty, "purchase_price": price}}
            "BOND": {},
            "ETF_MF": {},
        }

    def check_stock_eligibility(self, ticker: str):
        """Validates stock constraints: Price >= $3.00 and Market Cap >= $25M."""
        try:
            # 1. Check Price via Quote endpoint
            quote = finnhub_client.quote(ticker.upper())
            price = quote.get("c", 0.0)

            # 2. Check Market Cap via Profile2 endpoint
            profile = finnhub_client.company_profile2(symbol=ticker.upper())
            market_cap_millions = profile.get("marketCapitalization", 0.0)

            print(
                f"\n--- Validation for {ticker.upper()} ---"
            )
            print(f"Current Price: ${price:.2f}")
            print(f"Market Cap: ${market_cap_millions:.2f} Million")

            # Apply constraints
            price_valid = price >= 3.00
            mcap_valid = market_cap_millions >= 25.0

            if not price_valid:
                print("❌ REJECTED: Stock price is under $3.00.")
            if not mcap_valid:
                print("❌ REJECTED: Market Cap is under $25 Million.")

            is_eligible = price_valid and mcap_valid
            if is_eligible:
                print("✅ ELIGIBLE for trade.")

            return is_eligible, price

        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return False, 0.0

    def buy_asset(self, category: str, ticker: str, shares: float):
        """Executes a buy trade if rules and cash allow."""
        category = category.upper()
        if category not in ["STOCK", "BOND", "ETF_MF"]:
            print("Invalid category. Must be 'STOCK', 'BOND', or 'ETF_MF'.")
            return

        # Stock specific eligibility check
        if category == "STOCK":
            eligible, price = self.check_stock_eligibility(ticker)
            if not eligible:
                return
        else:
            # Fetch generic quote price for ETF/Bonds
            quote = finnhub_client.quote(ticker.upper())
            price = quote.get("c", 0.0)

        total_cost = price * shares
        if total_cost > self.cash:
            print(
                f"❌ INSUFFICIENT CASH: Requires ${total_cost:,.2f}, Available: ${self.cash:,.2f}"
            )
            return

        # Deduct cash & store asset
        self.cash -= total_cost
        if ticker in self.portfolio[category]:
            self.portfolio[category][ticker]["shares"] += shares
        else:
            self.portfolio[category][ticker] = {
                "shares": shares,
                "purchase_price": price,
            }

        print(
            f"✅ SUCCESS: Bought {shares} shares of {ticker} at ${price:.2f}/share."
        )

    def validate_min_allocations(self):
        """Verifies $10k minimum requirement across mandatory asset classes."""
        allocations = {"STOCK": 0.0, "BOND": 0.0, "ETF_MF": 0.0}

        for category in allocations:
            for ticker, details in self.portfolio[category].items():
                quote = finnhub_client.quote(ticker)
                current_price = quote.get("c", details["purchase_price"])
                allocations[category] += current_price * details["shares"]

        print("\n=== Mandatory $10k Allocation Audit ===")
        for cat, amount in allocations.items():
            status = "✅ PASSED" if amount >= 10000.0 else "❌ FAILED (Under $10k)"
            print(f"{cat}: ${amount:,.2f} / $10,000.00 -> {status}")

        return all(amt >= 10000.0 for amt in allocations.values())


# Example Usage Demonstration
if __name__ == "__main__":
    game = PortfolioGameManager(initial_cash=100000.0)

    # 1. Test buying stock below constraints (e.g. Penny stock or tiny market cap)
    game.buy_asset("STOCK", "SNDL", 100)

    # 2. Buy valid assets to meet baseline game limits
    game.buy_asset("STOCK", "AAPL", 70)  # Stocks >= $10k
    game.buy_asset("ETF_MF", "SPY", 25)  # ETFs >= $10k
    game.buy_asset("BOND", "TLT", 110)  # Bond ETF >= $10k

    # 3. Audit game compliance rules
    game.validate_min_allocations()
