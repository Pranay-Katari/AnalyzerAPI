import urllib.parse, urllib.request, xml.etree.ElementTree as ET, html, ssl, certifi, re, time
from bs4 import BeautifulSoup
import requests
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
an = SentimentIntensityAnalyzer()
from refine import run
import numpy as np
import yfinance as yf
from fundamentals import get_fundamentals
import asyncio, aiohttp


extra_lex = {
    "lawsuit": -2.5, "litigation": -2.2, "allegation": -2.4, "allege": -2.0,
    "prosecution": -2.0, "indictment": -2.3, "fraud": -2.6, "scandal": -2.4,
    "subpoena": -2.1, "deposition": -1.8, "damages": -1.9,
    "injunction": -1.9, "restraining order": -2.0, "cease and desist": -1.8,
    "class action": -2.2, "arbitration": -1.5, "tribunal": -1.7,
    "criminal": -2.3, "felony": -2.2, "misdemeanor": -1.8, "guilty": -2.0,
    "convicted": -2.5, "sentenced": -2.3, "imprisoned": -2.8, "jailed": -2.6,
    "arrest": -2.4, "charged": -2.1, "indicted": -2.3, "prosecuted": -2.2,
    "embezzlement": -2.5, "money laundering": -2.7, "bribery": -2.6,
    "corruption": -2.8, "kickback": -2.4, "insider trading": -2.6,
    "tax evasion": -2.5, "ponzi": -3.0, "pyramid scheme": -2.8,
    "securities fraud": -2.7, "accounting fraud": -2.6, "wire fraud": -2.4,
    "violation": -2.2, "breach": -2.0, "non-compliance": -1.9, "infringement": -1.8,
    "sanction": -2.0, "ban": -1.8,
   "lie": -2.3, "unethical": -2.1, "immoral": -2.0,
    "corrupt": -2.8, "shady": -2.0, "questionable": -1.6,
    "suspicious": -1.7, "dubious": -1.8, "illegitimate": -2.2,
    "down":-1.5, "layoffs": -1.6, "termination": -1.4, "firing": -1.5,
    "downsizing": -1.3, "restructuring": -1.1, "union dispute": -1.5,
    "strike": -1.4, "walkout": -1.6, "labor violation": -1.9,
    "wage theft": -2.3, "overtime violation": -1.8,
    "decline": -1.8, "drop": -2.0, "fall": -1.9, "plunge": -2.5,
    "crash": -3.0, "collapse": -2.8, "slump": -2.1, "tank": -2.4,
    "loss": -2.0, "losses": -2.1, "deficit": -2.0, "shortfall": -1.9,
    "miss": -1.7, "underperform": -1.9, "weak": -1.5, "poor": -1.7,
    "revenue decline": -2.1, "earnings miss": -1.9, "profit warning": -2.3,
    "guidance cut": -2.0, "margin compression": -1.9, "writedown": -2.1,
    "overleveraged": -2.3, "default": -2.8, "delinquent": -2.2,
    "distressed": -2.5, "covenant breach": -2.3, "credit risk": -2.0,
    "bankruptcy": -3.0, "chapter 11": -2.8, "insolvency": -2.9,
    "liquidation": -2.7, "going concern": -2.2,
    "cash crunch": -2.3, "liquidity crisis": -2.6, "negative cash flow": -1.9,
    "cash shortage": -2.2, "funding gap": -2.0,
    "downgrade": -2.0, "junk status": -2.5, "sell": -2.0,
    "strong sell": -2.5, "bearish": -1.8, "price target cut": -1.8,
    "selloff": -2.2, "correction": -1.7, "bear market": -2.1,
    "recession": -2.4, "volatile": -1.5, "uncertainty": -1.4,
    "risk": -1.3, "high risk": -1.8, "headwinds": -1.6,
    "challenges": -1.4, "problems": -1.6, "troubles": -1.8,
    "accounting irregularities": -2.4, "restatement": -2.1,
    "investigation": -1.9, "fine": -1.8, "penalty": -1.9,  "compliance": 1.6, "settlement": 1.3, "resolved": 1.7, "exonerated": 2.2,
    "acquitted": 1.8, "innocent": 1.6, "justice": 1.6,
    "safety": 2.2, "safe": 1.8, "protection": 1.6, "safeguard": 1.6,
    "secured": 1.6, "positive environment": 1.5, "improvement": 2.0,
    "strengthen": 1.9, "transparent": 1.6, "reform": 2.0, "ethical": 1.6,
    "expand": 3.2, "bullish": 2.7, "bull": 2.7, "higher": 2.5, "high": 2.5,
    "growth": 2.2, "record": 2.0, "innovation": 2.5, "resilient": 2.0,
    "strong": 2.2, "recovery": 2.0, "opportunity": 1.8,
    "outperform": 2.4, "beat expectations": 2.6, "surge": 2.4,
    "rally": 2.6, "all-time high": 2.9, "momentum": 2.1,
    "breakthrough": 2.4, "expansion": 2.3, "upgrade": 2.2,
    "buy": 2.0, "strong buy": 2.7, "dividend increase": 2.2,
    "profit": 2.0, "earnings beat": 2.5, "revenue growth": 2.3,
    "guidance raise": 2.3, "market share": 2.0,
    "competitive advantage": 2.2, "synergy": 2.0,
    "record quarter": 2.5, "historic": 2.4,
    "leadership": 1.8, "vision": 1.7, "execution": 1.6,
    "collaboration": 1.9, "partnership": 2.0, "alliance": 1.8,
    "strategic": 1.5, "long-term": 1.4, "sustainable": 1.9,
    "resiliency": 1.8, "efficiency": 1.7, "productivity": 1.8,
    "expanding": 2.0, "scaling": 2.1, "launch": 2.0,
    "new product": 2.2, "innovation pipeline": 2.5,
    "IPO": 2.0, "merger": 1.9, "acquisition": 1.8,
    "synergies": 2.0, "integration": 1.6,
    "customer satisfaction": 2.0, "client growth": 2.1,
    "brand strength": 1.9, "trust": 2.0, "loyalty": 1.8,
    "pipeline": 1.7, "milestone": 1.8, "achievement": 2.0,
    "progress": 2.0, "positive outlook": 2.5,
    "confidence": 2.0, "optimism": 2.3,
    "guidance increase": 2.4, "forecast raise": 2.3,
    "expansion plan": 2.2, "roadmap": 1.8, "booming": 2.5, "accelerating": 2.3, "record-breaking": 2.6,
    "scaling up": 2.0, "leading": 1.9, "dominant": 2.3,
    "pioneering": 2.4, "trailblazing": 2.5, "cutting-edge": 2.2,
    "disruptive": 2.1, "innovative": 2.5, "game-changing": 2.6,
    "groundbreaking": 2.5, "transformative": 2.4, "revolutionary": 2.6,
    "successful": 2.2, "profitable": 2.3, "lucrative": 2.1,
    "robust": 2.1, "strong performance": 2.5,
    "growth engine": 2.3, "expansive": 2.0, "positive momentum": 2.4,
    "tailwinds": 1.9, "bull market": 2.2, "optimistic": 2.3,
    "confidence high": 2.4, "record profits": 2.6,
    "exceeded expectations": 2.7, "beat estimates": 2.6,
    "stellar": 2.5, "exceptional": 2.6, "remarkable": 2.4,
    "impressive": 2.3, "outstanding": 2.5, "extraordinary": 2.6,
    "strategic win": 2.2, "major milestone": 2.4,
    "trusted": 2.0, "reputable": 1.9, "esteemed": 2.0,
    "well-positioned": 2.2, "competitive edge": 2.3,
    "leading position": 2.2, "market leader": 2.5,
    "award-winning": 2.6, "top-performing": 2.4,
    "synergy realized": 2.3, "strong demand": 2.5,
    "expanding footprint": 2.2, "scalable": 2.1,
    "innovative solution": 2.5, "visionary": 2.4,
    "successful launch": 2.5, "highly profitable": 2.6,
    "all-time record": 2.7, "boost": 2.2, }

an.lexicon.update(extra_lex)


TICKER_MAP = {
    "Apple Inc.": "AAPL", "Microsoft Corporation": "MSFT", "Amazon.com, Inc.": "AMZN",
    "NVIDIA Corporation": "NVDA", "Alphabet Inc. (Class A)": "GOOGL", "Alphabet Inc. (Class C)": "GOOG",
    "Meta Platforms, Inc.": "META", "Tesla, Inc.": "TSLA", "Adobe Inc.": "ADBE",
    "Salesforce, Inc.": "CRM", "Oracle Corporation": "ORCL", "Intel Corporation": "INTC",
    "Advanced Micro Devices, Inc.": "AMD", "IBM": "IBM", "Cisco Systems, Inc.": "CSCO",
    "Broadcom Inc.": "AVGO", "Qualcomm Incorporated": "QCOM", "Shopify Inc.": "SHOP",
    "ServiceNow, Inc.": "NOW", "Snowflake Inc.": "SNOW",
    "JPMorgan Chase & Co.": "JPM", "Bank of America Corporation": "BAC", "Citigroup Inc.": "C",
    "Wells Fargo & Company": "WFC", "Goldman Sachs Group, Inc.": "GS", "Morgan Stanley": "MS",
    "Charles Schwab Corporation": "SCHW", "American Express Company": "AXP", "BlackRock, Inc.": "BLK",
    "Visa Inc.": "V", "Mastercard Incorporated": "MA", "PayPal Holdings, Inc.": "PYPL",
    "Johnson & Johnson": "JNJ", "Pfizer Inc.": "PFE", "Merck & Co., Inc.": "MRK",
    "AbbVie Inc.": "ABBV", "Eli Lilly and Company": "LLY", "Amgen Inc.": "AMGN",
    "Gilead Sciences, Inc.": "GILD", "Moderna, Inc.": "MRNA", "Bristol Myers Squibb": "BMY",
    "UnitedHealth Group Incorporated": "UNH", "CVS Health Corporation": "CVS",
    "Walmart Inc.": "WMT", "Costco Wholesale Corporation": "COST", "The Home Depot, Inc.": "HD",
    "Target Corporation": "TGT", "Nike, Inc.": "NKE", "Starbucks Corporation": "SBUX",
    "McDonald's Corporation": "MCD", "The Coca-Cola Company": "KO", "PepsiCo, Inc.": "PEP",
    "Procter & Gamble Company": "PG", "Colgate-Palmolive Company": "CL",
    "The Boeing Company": "BA", "Caterpillar Inc.": "CAT", "General Electric Company": "GE",
    "3M Company": "MMM", "Lockheed Martin Corporation": "LMT", "Northrop Grumman Corporation": "NOC",
    "Honeywell International Inc.": "HON", "Raytheon Technologies Corporation": "RTX", "Deere & Company": "DE",
    "United Parcel Service, Inc.": "UPS", "FedEx Corporation": "FDX",
    "Exxon Mobil Corporation": "XOM", "Chevron Corporation": "CVX", "ConocoPhillips": "COP",
    "Schlumberger Limited": "SLB", "Halliburton Company": "HAL", "Baker Hughes Company": "BKR",
    "Phillips 66": "PSX", "Valero Energy Corporation": "VLO",
    "NextEra Energy, Inc.": "NEE", "Duke Energy Corporation": "DUK", "Dominion Energy, Inc.": "D",
    "Southern Company": "SO", "Exelon Corporation": "EXC", "American Electric Power Company, Inc.": "AEP",
    "Verizon Communications Inc.": "VZ", "AT&T Inc.": "T", "T-Mobile US, Inc.": "TMUS",
    "Comcast Corporation": "CMCSA", "Charter Communications, Inc.": "CHTR",
    "Airbnb, Inc.": "ABNB", "Uber Technologies, Inc.": "UBER", "Lyft, Inc.": "LYFT",
    "Delta Air Lines, Inc.": "DAL", "American Airlines Group Inc.": "AAL", "United Airlines Holdings, Inc.": "UAL",
    "Marriott International, Inc.": "MAR", "Hilton Worldwide Holdings Inc.": "HLT"
}


def get_name(company_name: str) -> str:
    return TICKER_MAP.get(company_name, company_name)


an.lexicon.update(extra_lex)

ctx = ssl.create_default_context(cafile=certifi.where())


def get_article_url(google_rss_url):
    response = requests.get(google_rss_url)
    soup = BeautifulSoup(response.text, "html.parser")
    data = soup.select_one('c-wiz[data-p]')['data-p']
    obj = json.loads(data.replace('%.@.', '["garturlreq",'))
    payload = {
        'f.req': json.dumps([[['Fbv4je', json.dumps(obj[:-6] + obj[-2:]), 'null', 'generic']]])
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
    }
    post_response = requests.post(
        'https://news.google.com/_/DotsSplashUi/data/batchexecute',
        data=payload,
        headers=headers
    )
    cleaned_data = post_response.text.replace(")]}'", "")
    array_string = json.loads(cleaned_data)[0][2]
    article_url = json.loads(array_string)[1]
    return article_url

async def fetch(session, url, timeout=8):
    try:
        async with session.get(url, timeout=timeout) as resp:
            return await resp.text()
    except:
        return ""

async def fetch_articles(article_urls):
    async with aiohttp.ClientSession(headers={"User-Agent": "Mozilla/5.0"}) as session:
        tasks = [fetch(session, u) for u in article_urls]
        return await asyncio.gather(*tasks)


def extract_article_text(html_data: str):
    try:
        soup = BeautifulSoup(html_data, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        candidates = []
        main = soup.find("main")
        if main:
            candidates.extend(main.find_all("p"))
        article = soup.find("article")
        if article:
            candidates.extend(article.find_all("p"))
        if not candidates:
            candidates = soup.find_all("p")
        text = " ".join(p.get_text(" ", strip=True) for p in candidates)
        return re.sub(r"\s+", " ", text).strip()
    except Exception:
        return ""


async def company_data(company_name):
    timestamps = (list(run(get_name(company_name))["ds"]))
    timestamps = [ts.strftime("%Y-%m-%d") for ts in timestamps]
    future_closings = (list(run(get_name(company_name))["y_hat"]))
    q = f"{company_name} stock OR {company_name} when:7d"
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({
        "q": q, "hl": "en-US", "gl": "US", "ceid": "US:en"
    })
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req, context=ctx, timeout=20).read().decode()
    root = ET.fromstring(data)

    count, sentiment = 0, 0
    published_link, date_published, titles = [], [], []

    rss_items = root.findall(".//item")[:10]
    titles = [html.unescape(i.findtext("title") or "") for i in rss_items]
    raw_urls = [i.findtext("link") or "" for i in rss_items]
    urls = [get_article_url(u) for u in raw_urls]
    dates = [i.findtext("pubDate") or "n/a" for i in rss_items]

    pages = await fetch_articles(urls)

    sentiment, published_link, date_published = 0, [], []
    for i, page in enumerate(pages):
        text = extract_article_text(page)
        if not text:
            text = titles[i]
        sentiment += an.polarity_scores(text)["compound"]
        published_link.append(urls[i])
        date_published.append(dates[i])

    sentiment = sentiment / max(len(rss_items), 1)


    ticker = yf.Ticker(get_name(company_name))
    info = ticker.info
    hist = ticker.history(period="6mo")

    past_dates = hist.index.strftime("%Y-%m-%d").tolist()
    past_closings = hist["Close"].tolist()

    returns = hist['Close'].pct_change().dropna()
    volatility = returns.std() * np.sqrt(252)

    extra_fundamentals = {
        "peg_ratio": info.get("pegRatio"),
        "price_to_book": info.get("priceToBook"),
        "market_cap": info.get("marketCap"),
        "beta": info.get("beta"),
        "volatility_6m": volatility,
        "revenue_growth": info.get("revenueGrowth"),
        "eps_growth_q": info.get("earningsQuarterlyGrowth"),
        "dividend_yield": info.get("dividendYield"),
        "payout_ratio": info.get("payoutRatio"),
        "ma_50": info.get("fiftyDayAverage"),
        "ma_200": info.get("twoHundredDayAverage")
    }

    fundamentals = get_fundamentals(company_name)
    fundamentals.update(extra_fundamentals)

    pe = info.get("trailingPE")
    peg = info.get("pegRatio")
    pb = info.get("priceToBook")

    if pe and (pe < 15 or (peg and peg < 1) or (pb and pb < 1)):
        valuation_label = "Undervalued"
    elif pe and (pe > 30 or (peg and peg > 2)):
        valuation_label = "Overvalued"
    else:
        valuation_label = "Fairly Valued"

    fundamentals["valuation_label"] = valuation_label

    data = {
        "company_name": company_name,
        "links": published_link,
        "titles": titles,
        "dates": date_published,
        "overall_sentiment": sentiment,
        "future_closings": future_closings,
        "closing_timestamps": timestamps,
        "past_dates": past_dates,
        "past_closings": past_closings,
        "fundamentals": fundamentals
    }

    return data
