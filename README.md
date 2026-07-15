# pyBuffet

EDGAR Ledger — a single-file dashboard that pulls company financials (income statement, balance sheet, cash flow) straight from SEC EDGAR's free XBRL APIs, plus a tiny stdlib relay that satisfies the SEC's declared User-Agent requirement.

## Quick start

1. Open `edgar_relay.py` and set `IDENTITY` to your contact email (the SEC wants to know who is calling).
2. Run the relay from this folder — no packages needed:

   ```
   python edgar_relay.py
   ```

   It serves the dashboard at http://127.0.0.1:8787/ and forwards SEC calls with the proper header.
3. In the dashboard, load a watchlist: drop in your own `.json` or click **Load the example list** (the bundled `investments.json`).

## Watchlist format

The dashboard asks for a `.json` file shaped like `investments.json`:

```json
{
  "investments": [
    {
      "company": "Micron Technology",
      "category": "RAM",
      "ticker": "MU",
      "exchange": "NASDAQ",
      "country": "United States",
      "date_spotted": "01/02/2026"
    }
  ]
}
```

All six keys are strings. Use `"NONE"` where a field doesn't apply (e.g. `exchange` for indices, commodities, FX or crypto) and `MM/DD/YYYY` or `"NONE"` for `date_spotted`. Entries in the same `category` should sit next to each other — the sidebar groups them in order.

## Building a list with an AI

Open the **Build a list (AI)** tab in the dashboard. Copy the prompt shown there into any AI assistant (Claude, ChatGPT, Gemini, …), then paste your own list of companies / tickers / notes directly underneath the prompt and send it. Save the AI's JSON reply as a `.json` file and load it from the Ledger tab.

## Warren Buffett tab

The **Warren Buffett** tab holds chapter notes from *Warren Buffett and the Interpretation of Financial Statements* (chapters 1–13). Each card shows the chapter number, title and summary; select a chapter to read it in full, with its income-statement exhibits and previous/next navigation. The content lives in `buffett_book_ch113.json` and is embedded in the page so it works offline.

## Files

| File | What it is |
|---|---|
| `edgar-ledger.html` | The dashboard — watchlist sidebar, financials ledger, AI prompt tab, Buffett chapter notes |
| `edgar_relay.py` | Local relay/server (stdlib only) that adds the SEC User-Agent header |
| `investments.json` | Example watchlist in the expected format |
| `buffett_book_ch113.json` | Chapter notes shown in the Warren Buffett tab |
