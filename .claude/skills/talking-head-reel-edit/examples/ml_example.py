"""Train two small real models (churn, loan) and export numbers + confusion-matrix PNGs for the notebook screens.
Usage: python3 -I ml.py <out_dir> <fonts_dir>"""
import json, sys, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score
OUT = sys.argv[1]; FONTS = sys.argv[2]
fm.fontManager.addfont(f'{FONTS}/Inter_wght_600.ttf'); plt.rcParams['font.family'] = 'Inter'
rng = np.random.default_rng(7)


def loan(n=12000):
    income = rng.lognormal(10.9, 0.45, n).round(-2)            # monthly rupees
    spend = np.clip(rng.normal(0.55, 0.18, n), 0.1, 1.3)        # spend / income
    bills = np.clip(rng.normal(0.86, 0.12, n), 0.3, 1.0)        # on-time bill ratio
    upi = rng.poisson(38, n)                                     # UPI txns / month
    job = np.clip(rng.gamma(2.2, 2.0, n), 0, 30).round(1)       # years in job
    cibil = np.clip(rng.normal(715, 55, n), 300, 900).round()
    z = (-1.2 + 2.4 * (spend - 0.55) - 5.0 * (bills - 0.86) - 0.12 * (job - 4.4) - 0.006 * (cibil - 715)
         - 0.45 * (np.log(income) - 10.9) - 0.01 * (upi - 38) + rng.normal(0, 0.55, n))
    default = (rng.random(n) < 1 / (1 + np.exp(-z))).astype(int)
    df = pd.DataFrame(dict(income=income, spend_ratio=spend.round(2), bills_on_time=bills.round(2),
                           upi_txns=upi, job_years=job, cibil=cibil, default=default))
    df.loc[rng.random(n) < 0.04, 'job_years'] = np.nan
    df.loc[rng.random(n) < 0.03, 'income'] = np.nan
    return df, 'default'


def churn(n=10000):
    tenure = rng.integers(1, 72, n); monthly = rng.normal(820, 260, n).clip(199, 2499).round()
    tickets = rng.poisson(1.4, n); usage = rng.normal(14, 6, n).clip(0, 40).round(1)
    contract = rng.choice(['monthly', 'yearly', '2-year'], n, p=[.55, .3, .15])
    z = (0.6 - 0.05 * tenure + 0.0012 * (monthly - 820) + 0.45 * tickets - 0.06 * (usage - 14)
         - 1.1 * (contract == 'yearly') - 1.8 * (contract == '2-year') + rng.normal(0, .6, n))
    churned = (rng.random(n) < 1 / (1 + np.exp(-z))).astype(int)
    df = pd.DataFrame(dict(tenure=tenure, monthly_bill=monthly, support_tickets=tickets, usage_hrs=usage,
                           contract=contract, churn=churned))
    df.loc[rng.random(n) < 0.035, 'usage_hrs'] = np.nan
    return df, 'churn'


res = {}
for name, (df, y) in [('loan', loan()), ('churn', churn())]:
    res[name] = dict(rows=len(df), nulls={k: int(v) for k, v in df.isnull().sum().items() if v},
                     head=df.head(5).to_dict(orient='records'), cols=list(df.columns))
    d = df.dropna().copy()
    if 'contract' in d: d = pd.get_dummies(d, columns=['contract'], drop_first=True)
    X, Y = d.drop(columns=[y]), d[y]
    Xtr, Xte, ytr, yte = train_test_split(X, Y, test_size=0.2, random_state=42, stratify=Y)
    clf = RandomForestClassifier(n_estimators=300, max_depth=9, random_state=42, n_jobs=-1).fit(Xtr, ytr)
    p = clf.predict(Xte); cm = confusion_matrix(yte, p)
    res[name].update(clean_rows=len(d), acc=round(accuracy_score(yte, p), 4), prec=round(precision_score(yte, p), 4),
                     rec=round(recall_score(yte, p), 4), cm=cm.tolist(), n_test=len(yte),
                     importances=sorted(zip(X.columns, clf.feature_importances_.round(3).tolist()), key=lambda x: -x[1]))
    if name == 'loan':   # two demo applicants scored by the real model
        demo = pd.DataFrame([dict(income=68000, spend_ratio=0.42, bills_on_time=0.97, upi_txns=52, job_years=6.0, cibil=742),
                             dict(income=31000, spend_ratio=0.93, bills_on_time=0.61, upi_txns=19, job_years=0.8, cibil=700)])
        res[name]['demo_risk'] = (clf.predict_proba(demo[X.columns])[:, 1] * 100).round(0).tolist()
    else:
        demo = pd.DataFrame([dict(tenure=4, monthly_bill=1290, support_tickets=4, usage_hrs=5.5,
                                  **{c: 0 for c in X.columns if c.startswith('contract_')})])
        res[name]['demo_risk'] = (clf.predict_proba(demo[X.columns])[:, 1] * 100).round(0).tolist()
    labels = ['Repaid', 'Default'] if name == 'loan' else ['Stayed', 'Churned']
    fig, ax = plt.subplots(figsize=(4.4, 3.8), dpi=200); fig.patch.set_facecolor('#1e1e2e'); ax.set_facecolor('#1e1e2e')
    ax.imshow(cm, cmap='YlOrBr')
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f'{cm[i, j]}', ha='center', va='center', fontsize=17,
                    color='#fff' if cm[i, j] > cm.max() * .45 else '#111')
    ax.set_xticks([0, 1], labels, color='#cdd6f4', fontsize=11)
    ax.set_yticks([0, 1], labels, color='#cdd6f4', fontsize=11, rotation=90, va='center')
    ax.set_xlabel('Predicted', color='#a6adc8', fontsize=11); ax.set_ylabel('Actual', color='#a6adc8', fontsize=11)
    ax.set_title('Confusion Matrix', color='#f5e0dc', fontsize=13, pad=10)
    for s in ax.spines.values(): s.set_visible(False)
    ax.tick_params(length=0); fig.tight_layout()
    fig.savefig(f'{OUT}/cm_{name}.png', facecolor=fig.get_facecolor()); plt.close(fig)
json.dump(res, open(f'{OUT}/ml.json', 'w'), indent=1, default=str)
for k, v in res.items():
    print(k, v['rows'], v['nulls'], v['clean_rows'], 'acc', v['acc'], 'cm', v['cm'], v.get('demo_risk'), v['importances'][:3])
