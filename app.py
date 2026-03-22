import streamlit as st
# =========================
# パスワード認証
# =========================
PASSWORD = "1234"  # ←好きなパスワードに変更

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐パスワードを入力してください")

    pw = st.text_input("パスワード", type="password")

    if pw == PASSWORD:
        st.session_state.auth = True
        st.rerun()
    elif pw != "":
        st.error("パスワードが違います")

    st.stop()
import pandas as pd
import yfinance as yf

st.set_page_config(
    layout="wide",
    page_title="Smart Stock"
)

# =========================
# CSS（デザイン）
# =========================
st.markdown("""
<style>

/* 背景 */
.stApp {
    background-color: #F8FAFC;
}

/* フォント */
html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

/* 見出し */
h1, h2, h3 {
    color: #111827;
    font-weight: 700;
}

/* カード */
.card {
    background: white;
    padding: 20px;
    border-radius: 14px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    margin-bottom: 20px;
}

/* ボタン */
.stButton>button {
    background-color: #2563EB;
    color: white;
    border-radius: 10px;
    padding: 10px 18px;
    font-weight: 600;
    border: none;
}

.stButton>button:hover {
    background-color: #1d4ed8;
}

/* 入力 */
.stTextInput input {
    border-radius: 10px;
}

/* バッジ */
.badge {
    background:#2563eb;
    color:white;
    padding:4px 8px;
    border-radius:6px;
    font-size:12px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# ロゴ
# =========================
st.markdown("""
<div style="display:flex; align-items:center; gap:10px;">
<div style="
width:40px;
height:40px;
background:#2563eb;
border-radius:10px;
display:flex;
align-items:center;
justify-content:center;
color:white;
font-weight:bold;
">
S
</div>
<h2 style="margin:0;">Smart Stock</h2>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# 説明
# =========================
st.markdown("""
<div class="card">
🚀 <b>AIが有望銘柄を自動抽出</b><br>
何も入力せず、毎日のチャンスを確認できます
</div>
""", unsafe_allow_html=True)

# =========================
# 更新ボタン
# =========================
col1, col2 = st.columns([1,3])
refresh = col1.button("🔄 更新")

if refresh:
    st.cache_data.clear()
    st.success("データ更新しました")

st.info("📅 毎日更新：朝チェック推奨")

# =========================
# スコア説明
# =========================
with st.expander("📘 スコアの見方"):
    st.write("""
    ・50以上：上昇トレンド  
    ・100：強い上昇＋加速  
    ・0：様子見  
    """)

# =========================
# 入力
# =========================
st.subheader("📥 個別分析（任意）")

codes = st.text_input("例：7203.T,6758.T", "")
run = st.button("分析")

# =========================
# 銘柄リスト
# =========================
auto_symbols = [
    "7203.T","6758.T","9984.T","9432.T","8306.T",
    "6501.T","6861.T","4063.T","8035.T","8058.T"
]

# =========================
# 名前取得
# =========================
def get_name(symbol):
    try:
        return yf.Ticker(symbol).info.get("shortName", symbol)
    except:
        return symbol

# =========================
# 分析
# =========================
@st.cache_data(ttl=300)
def analyze(symbol):

    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="3mo")

        if df.empty:
            return None

        df["MA5"] = df["Close"].rolling(5).mean()
        df["MA25"] = df["Close"].rolling(25).mean()

        latest = df.iloc[-1]

        price = latest["Close"]
        ma5 = latest["MA5"]
        ma25 = latest["MA25"]

        change = (df["Close"].iloc[-1] - df["Close"].iloc[-5]) / df["Close"].iloc[-5] * 100

        score = 0
        reason = []

        if ma5 > ma25:
            score += 50
            reason.append("上昇")

        if change > 3:
            score += 50
            reason.append("上昇加速")

        return {
            "銘柄": symbol,
            "銘柄名": get_name(symbol),
            "株価": round(price, 0),
            "スコア": score,
            "理由": "・".join(reason),
            "上昇率": round(change,1),
            "df": df
        }

    except:
        return None

# =========================
# 自動分析
# =========================
results = []

for s in auto_symbols:
    with st.spinner(f"{s}分析中..."):
        data = analyze(s)
        if data:
            results.append(data)

# =========================
# 表示
# =========================
if results:

    df = pd.DataFrame(results).sort_values("スコア", ascending=False)

    # 注目銘柄
    top = df.iloc[0]

    st.markdown(f"""
    <div class="card">
    <h3>🔥 本日の注目銘柄</h3>

    <b style="font-size:20px;">
    {top['銘柄名']}（{top['銘柄']}）
    </b><br><br>

    💰 株価：{top['株価']}円<br>
    📊 スコア：<span class="badge">{top['スコア']}</span><br>
    📈 上昇率：{top['上昇率']}%<br><br>

    🧠 {top['理由']}<br><br>

    👉 <b style="color:#2563EB;">短期上昇トレンド</b>
    </div>
    """, unsafe_allow_html=True)

    # チャート
    st.line_chart(top["df"]["Close"])

    # ランキング
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📊 ランキング")

    df["順位"] = range(1, len(df)+1)
    display_df = df[["順位","銘柄名","株価","スコア"]]

    st.dataframe(display_df, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # 急騰候補
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🚀 急騰候補")

    breakout = df[df["上昇率"] > 5]

    if not breakout.empty:
        st.success("上昇加速銘柄あり")
        st.dataframe(breakout[["銘柄名","株価","上昇率"]], use_container_width=True)
    else:
        st.info("該当なし")

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# 個別分析
# =========================
if run and codes:

    st.subheader("📊 個別分析")

    symbols = [s.strip() for s in codes.split(",") if s.strip()]
    results = []

    for s in symbols:
        with st.spinner(f"{s}分析中..."):
            data = analyze(s)
            if data:
                results.append(data)

    if results:
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.error("銘柄コードを確認してください")

# =========================
# フッター
# =========================
st.markdown("""
---
💡 Smart Stock  
AIによる銘柄分析ツール
""")
