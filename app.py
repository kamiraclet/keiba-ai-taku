import streamlit as st
import pandas as pd
import plotly.express as px
import glob
import io
import re

# 1. SEOを意識したページ設定
st.set_page_config(
    page_title="競馬AIタク | データサイエンスが導く予測勝率と期待値の最終結論", 
    page_icon="🏇", 
    layout="wide"
)

# --- カスタムCSS（デザイン調整） ---
style = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .main .block-container {
        max-width: 1000px;
        padding-top: 2rem;
        margin: auto;
    }

    .title-container {
        text-align: center;
        padding-bottom: 2rem;
        border-bottom: 2px solid #f0f2f6;
        margin-bottom: 2rem;
    }

    /* タブメニューの中央寄せ */
    .stTabs [data-baseweb="tab-list"] {
        display: flex;
        justify-content: center;
        gap: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #006400 !important;
        color: white !important;
    }
    
    /* フッターのデザイン */
    .custom-footer {
        margin-top: 5rem;
        padding: 2rem;
        border-top: 1px solid #eee;
        text-align: center;
        color: #888;
        font-size: 0.8rem;
    }
</style>
"""
st.markdown(style, unsafe_allow_html=True)

# --- サイトヘッダー ---
st.markdown("""
<div class="title-container">
    <h1 style='font-size: 3rem; color: #1a3321; margin-bottom: 0;'>🏇 競馬AIタク</h1>
    <p style='font-size: 1.2rem; color: #444; font-weight: bold; margin-top: 10px;'>
        〜 30年分のビッグデータが導く「勝つための期待値」を全レース無料公開 〜
    </p>
</div>
""", unsafe_allow_html=True)

# --- メインメニュー（タブ） ---
# 「ポリシー」を削除し、コンテンツに特化させました
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "👤 開発者紹介", 
    "🤖 競馬AIについて",
    "📊 予測勝率公開", 
    "🏆 レース特集", 
    "📚 会場データ", 
    "📄 競馬コラム"
])

# --- 各メニューの内容 ---

with tab1:
    col_p1, col_p2, col_p3 = st.columns([1, 2, 1])
    with col_p2:
        st.markdown("<h2 style='text-align: center;'>AI予想家タク プロフィール</h2>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center;'><img src='https://www.jp-p.jp/images/common/horse_icon.png' width='100'></div>", unsafe_allow_html=True)
        st.write("""
        **【データと理論を融合させた真実の追求】**
        netkeibaやX(旧Twitter)、note等のプラットフォームで活動するデータサイエンティスト。
        独自モデルによる期待値投資を提唱しています。
        """)

with tab2:
    st.markdown("<h2 style='text-align: center;'>🤖 競馬AIタクのロジック</h2>", unsafe_allow_html=True)
    st.write("独自に開発した深層学習モデルを用い、多角的に解析した予測勝率を算出しています。")

with tab3:
    st.markdown("<h2 style='text-align: center;'>📈 最新レース予測勝率</h2>", unsafe_allow_html=True)
    files = glob.glob("*.csv")
    if not files:
        st.info("現在、最新データを解析中です。しばらくお待ちください。")
    else:
        df_list = []
        for f in files:
            try:
                with open(f, 'rb') as b: data = b.read()
                for enc in ['cp932', 'utf-8', 'shift_jis']:
                    try:
                        tmp = pd.read_csv(io.BytesIO(data), encoding=enc)
                        df_list.append(tmp)
                        break
                    except: continue
            except Exception: continue
        if df_list:
            df = pd.concat(df_list).drop_duplicates()
            df.columns = df.columns.str.strip()
            df['開催場所'] = df['開催'].str.replace(r'\d+R$', '', regex=True)
            df['表示用レース名'] = df['開催'].str.extract(r'(\d+R)$').fillna('') + " " + df['レース名']

            c1, c2, c3 = st.columns(3)
            with c1: selected_date = st.selectbox("📅 開催日", sorted(df['日付'].unique(), reverse=True))
            with c2: selected_venue = st.selectbox("📍 開催場所", sorted(df[df['日付'] == selected_date]['開催場所'].unique()))
            with c3: selected_race = st.selectbox("🏁 レース", df[(df['日付'] == selected_date) & (df['開催場所'] == selected_venue)]['表示用レース名'].unique())

            target_df = df[(df['表示用レース名'] == selected_race) & (df['開催場所'] == selected_venue) & (df['日付'] == selected_date)].sort_values("予想順位")
            if not target_df.empty:
                fig = px.bar(target_df, x='馬名', y='勝率', color='勝率', text_auto='.1f', color_continuous_scale='Greens')
                st.plotly_chart(fig, width='stretch')
                display_table = target_df[['予想順位', '馬番', '馬名', '勝率']].copy()
                display_table['勝率'] = display_table['勝率'].map('{:.1f}%'.format)
                display_table['馬番'] = display_table['馬番'].fillna('-').apply(lambda x: str(int(x)) if isinstance(x, float) else str(x))
                st.dataframe(display_table, hide_index=True, width='stretch')

with tab4:
    st.markdown("<h2 style='text-align: center;'>🏆 重賞レース徹底分析</h2>", unsafe_allow_html=True)
    st.write("準備中：今週末の重賞レースに関するAIの見解を公開します。")

with tab5:
    st.markdown("<h2 style='text-align: center;'>📚 競馬場別・データ傾向分析</h2>", unsafe_allow_html=True)
    st.write("準備中：各競馬場別のAI解析による特注データを公開予定です。")

with tab6:
    st.markdown("<h2 style='text-align: center;'>📄 競馬AIタク・コラム</h2>", unsafe_allow_html=True)
    st.write("準備中：AI予想の仕組みや、期待値投資の重要性について綴ります。")

# --- フッター（ここにプライバシーポリシーを配置） ---
st.markdown("""
<div class="custom-footer">
    <p>© 2026 競馬AIタク - Data Science Horse Racing Prediction</p>
    <div style="max-width: 800px; margin: 0 auto; text-align: left; background: #fdfdfd; padding: 20px; border-radius: 8px; border: 1px solid #eee;">
        <strong style="font-size: 0.9rem;">【プライバシーポリシー & 免責事項】</strong><br>
        <span style="font-size: 0.75rem;">
        <b>1. 広告の配信について：</b>当サイトでは第三者配信の広告サービスを利用することがあります。ユーザーの興味に応じた広告表示のためクッキー（Cookie）を使用することがあります。<br>
        <b>2. 免責事項：</b>本サイトのデータはAIによる算出結果であり的中を保証するものではありません。馬券購入は自己責任で行ってください。情報の利用による損害について一切の責任を負いません。
        </span>
    </div>
</div>
""", unsafe_allow_html=True)
