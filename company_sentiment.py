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
    "suspension": -1.7, "revocation": -2.1, "probation": -1.6,
    "censure": -1.8, "reprimand": -1.5, "warning": -1.3,
    "misconduct": -2.2, "malpractice": -2.3, "negligence": -2.0,
    "reckless": -2.1, "willful": -1.9, "intentional": -1.7,
    "coverup": -2.2, "concealment": -2.0, "obstruction": -2.1,
    "tampering": -2.3, "destruction of evidence": -2.5,
    "abuse": -3.2, "sexually":-3, "harassment": -2.5, "discrimination": -2.4,
    "exploitation": -3.0, "predator": -3.0, "assault": -3.2,
    "sexual harassment": -3.0, "hostile environment": -2.2,
    "retaliation": -2.1, "intimidation": -2.0, "coercion": -2.3,
    "unsafe": -2.2, "hazardous": -2.1, "toxic": -2.0, "contamination": -2.3,
    "exposure": -1.9, "endanger": -2.4, "harm": -1.8,
    "injury": -2.0, "death": -2.8, "fatality": -2.9, "accident": -1.7,
    "defective": -2.0, "faulty": -1.8, "recall": -1.9,
    "hack": -2.2, "cybersecurity": -1.6,
    "privacy violation": -2.1, "unauthorized access": -2.0,
    "data theft": -2.4, "identity theft": -2.6, "phishing": -2.0,
    "pollution": -2.1, "spill": -2.0,
    "environmental damage": -2.2, "illegal dumping": -2.4,
    "emissions violation": -1.9, "groundwater contamination": -2.3,
    "manipulation": -2.5, "rigging": -2.6, "collusion": -2.4,
    "price fixing": -2.5, "monopoly": -1.8, "antitrust": -2.0,
    "cartel": -2.7, "conspiracy": -2.3,
    "probe": -1.7, "inquiry": -1.5,
    "audit": -1.3, "review": -1.1, "examination": -1.2,
    "scrutiny": -1.4, "surveillance": -1.6, "monitoring": -1.2,
    "failure": -1.8, "crisis": -2.0,
    "emergency": -1.7, "disaster": -2.3, "catastrophe": -2.8,
    "dishonest": -2.2, "deceptive": -2.1, "misleading": -1.9,
    "false": -2.0, "lie": -2.3, "unethical": -2.1, "immoral": -2.0,
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
    "investigation": -1.9, "fine": -1.8, "penalty": -1.9,
    "worthless": -3.0, "wipeout": -2.9, "catastrophic": -2.9,
    "complaint": -1.6, "dispute": -1.4, "grievance": -1.5,
    "refund": -1.2, "chargeback": -1.4, "dissatisfied": -1.3,
    "boycott": -1.8, "protest": -1.5, "backlash": -1.7,
    "rape": -4.0, "csam": -4.0, "trafficking": -3.5,
    "terrorism": -4.0, "murder": -4.0, "kidnapping": -3.8,
    "extortion": -2.9, "blackmail": -2.7, "racketeering": -3.0,
    "whistleblower": -1.5, "expose": -1.7, "leak": -1.9,
    "conflict of interest": -1.8, "insider": -1.6, "favoritism": -1.7,
    "nepotism": -1.9, "cronyism": -2.0, "patronage": -1.6,
    "undisclosed": -1.4, "hidden": -1.6, "secret": -1.3,

    "compliance": 1.2, "settlement": 0.8, "resolved": 1.0, "exonerated": 1.5,
    "acquitted": 1.3, "innocent": 1.2, "justice": 1.0,
    "safety": 1.4, "safe": 1.2, "protection": 1.0, "safeguard": 1.0,
    "secured": 1.0, "positive environment": 0.8, "improvement": 1.0,
    "strengthen": 0.9, "compliant": 1.0, "transparent": 0.8,
    "rehabilitation": 1.0, "reform": 1.2, "ethical": 1.0, "responsible": 0.9, "lifts":1.3,
    "expand":2.9, "bullish":2, "bull":2, "higher":2, "high":2,
}

TICKER_MAP = {
    # Tech
    "Apple Inc.": "AAPL",
    "Microsoft Corporation": "MSFT",
    "Amazon.com, Inc.": "AMZN",
    "NVIDIA Corporation": "NVDA",
    "Alphabet Inc. (Class A)": "GOOGL",
    "Alphabet Inc. (Class C)": "GOOG",
    "Meta Platforms, Inc.": "META",
    "Tesla, Inc.": "TSLA",
    "Visa Inc.": "V",
    "Mastercard Incorporated": "MA",
    "JPMorgan Chase & Co.": "JPM",
    "Bank of America Corporation": "BAC",
    "Citigroup Inc.": "C",
    "Wells Fargo & Company": "WFC",
    "Walmart Inc.": "WMT",
    "Procter & Gamble Company": "PG",
    "The Coca-Cola Company": "KO",
    "PepsiCo, Inc.": "PEP",
    "McDonald's Corporation": "MCD",
    "Nike, Inc.": "NKE",
    "The Home Depot, Inc.": "HD",
    "UnitedHealth Group Incorporated": "UNH",
    "Johnson & Johnson": "JNJ",
    "Pfizer Inc.": "PFE",
    "Merck & Co., Inc.": "MRK",
    "AbbVie Inc.": "ABBV",
    "Zoetis Inc.": "ZTS",
    "Exxon Mobil Corporation": "XOM",
    "Chevron Corporation": "CVX",
    "ConocoPhillips": "COP",
    "The Boeing Company": "BA",
    "Caterpillar Inc.": "CAT",
    "United Parcel Service, Inc.": "UPS",
    "General Electric Company": "GE",
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

def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, context=ctx, timeout=timeout)

def extract_article_text(article_url):
    try:
        resp = fetch(article_url)
        html_data = resp.read()
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
        text = re.sub(r"\s+", " ", text).strip()
        return text
    except Exception as e:
        return ""

def company_data(company_name):
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

    for item in root.findall(".//item")[:10]:
        title = html.unescape(item.findtext("title") or "")
        link = item.findtext("link") or ""
        pub = item.findtext("pubDate") or "n/a"
        publisher_url = get_article_url(link)

        article_text = extract_article_text(publisher_url) or title
        sentiment += an.polarity_scores(article_text)["compound"]
        count += 1

        published_link.append(publisher_url)
        date_published.append(pub)
        titles.append(title)

    sentiment = sentiment / max(count, 1)

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
        "past_dates": past_dates,              # ✅ new field
        "past_closings": past_closings,        # ✅ new field
        "fundamentals": fundamentals
    }

    return data
