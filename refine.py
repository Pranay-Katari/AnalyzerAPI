import numpy as np, pandas as pd, yfinance as yf
from sklearn.ensemble import GradientBoostingRegressor
from pandas.tseries.offsets import BDay

def run(company_name):
    c = yf.download(company_name, period="10y", interval="1d", auto_adjust=True, progress=False)["Close"].dropna()
    if isinstance(c, pd.DataFrame): c = c.iloc[:,0]
    df = pd.DataFrame({"ds": pd.to_datetime(c.index).tz_localize(None), "y": c.values.astype(float)})

    df["d1"] = df["y"].diff()
    df["d1_lag1"]  = df["d1"].shift(1)
    df["d1_mean5"] = df["d1"].rolling(5).mean().shift(1)
    df["d1_vol20"] = df["d1"].rolling(20).std().shift(1)
    df = df.dropna().reset_index(drop=True)

    X = df[["d1_lag1","d1_mean5","d1_vol20"]].to_numpy(float)
    y = df["d1"].to_numpy(float)

    gbr = GradientBoostingRegressor(random_state=42, n_estimators=800, learning_rate=0.04, max_depth=3, subsample=0.8)
    gbr.fit(X, y)

    def forecast(history, model, steps=100):
        w = history[["ds","y"]].copy(); w["d1"] = w["y"].diff()
        out = []
        for _ in range(steps):
            x = np.array([[float(w["d1"].iloc[-1]), float(w["d1"].tail(5).mean()), float(w["d1"].tail(20).std())]])
            d1 = float(model.predict(x)[0])
            ds = w["ds"].iloc[-1] + BDay(1)
            y_ = float(w["y"].iloc[-1] + d1)
            w.loc[len(w)] = {"ds": ds, "y": y_, "d1": d1}
            out.append({"ds": ds, "y_hat": y_, "d1_hat": d1})
        return pd.DataFrame(out)

    return forecast(df[["ds","y"]], gbr, steps=100)