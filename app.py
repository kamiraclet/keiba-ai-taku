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

# --- 洗練されたデザインのためのカスタムCSS ---
style = """
<style>
    /* 右上のメニュー・フッターを隠す */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 全体の中央寄せと最大幅の制限 */
    .main .block-container {
        max-width: 1000px;
        padding-top: 2rem;
        margin: auto;
    }

    /* タイトルセクションの中央寄せ */
    .title-container {
        text-align: center;
        padding-bottom: 2rem;
    }

    /* タブ（メニューバー）のデザイン調整 */
    .stTabs [data-baseweb="tab-list"] {
        display: flex;
        justify-content: center; /* メニューを中央寄せ */
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 5px 5px 0px 0px;
        gap: 1px;
        padding-left: 20px;
        padding-right: 20px;
        font-weight: bold;
    }
    /* アクティブなタブの色を競馬らしいグリーンに */
    .stTabs [aria-selected="true"] {
        background-color: #006400 !important;
        color: white !important;
    }

    /* セクションの見出し */
    h1, h2, h3 {
        color: #1a3321;
        text-align: center;
    }
</style>
"""
st.markdown(style, unsafe_allow_html=True)

# --- サイトヘッダー（SEO意識のキャッチコピー） ---
st.markdown("""
<div class="title-container">
    <h1 style='font-size: 2.5rem;'>🏇 競馬AIタク</h1>
    <p style='font-size: 1.1rem; color: #666;'>〜 30年分のビッグデータが導く「勝つための期待値」を全レース無料公開 〜</p>
</div>
""", unsafe_allow_html=True)

# --- メニュー（タブ）の設定：指示通りの順番 ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "👤 開発者紹介", 
    "📊 予測勝率公開", 
    "🏆 レース特集", 
    "📚 会場データ", 
    "📄 競馬コラム"
])

# --- 各メニューの内容 ---

# ① 開発者紹介
with tab1:
    col_p1, col_p2, col_p3 = st.columns([1, 2, 1])
    with col_p2:
        st.markdown("<h2 style='text-align: center;'>AI予想家タク プロフィール</h2>", unsafe_allow_html=True)
        st.image("https://www.jp-p.jp/images/common/horse_icon.png", width=150) # ここにご自身のロゴを
        st.write("""
        **【データサイエンス × 競馬への情熱】**
        
        競馬AIタクは、過去30年以上の膨大なレースデータをディープラーニング技術によって解析し、
        「感情を一切排除した客観的な勝率」を算出する次世代の予想システムです。
        
        「競馬はギャンブルではなく投資である」という信念のもと、
        知名度と権威性を備えたAI予想の第一人者を目指し、日々モデルのアップデートを続けています。
        """)

# ② 予測勝率公開
with tab2:
    st.markdown("<h2 style='text-align: center;'>📈 最新レース予測勝率</h2>", unsafe_allow_html=True)
    files = glob.glob("*.csv")

    if not files:
        st.info("現在、最新データを解析中です。しばらくお待ちください。")
    else:
        df_list = []
        for f in files:
            try:
                with open(f, 'rb') as b:
                    data = b.read()
                for enc in ['cp932', 'utf-8', 'shift_jis']:
                    try:
                        tmp = pd.read_csv(io.BytesIO(data), encoding=enc)
                        df_list.append(tmp)
                        break
                    except:
                        continue
            except Exception:
                continue

        if df_list:
            df = pd.concat(df_list).drop_duplicates()
            df.columns = df.columns.str.strip()
            df['開催場所'] = df['開催'].str.replace(r'\d+R$', '', regex=True)
            df['レース番号'] = df['開催'].str.extract(r'(\d+R)$')
            df['表示用レース名'] = df['レース番号'] + " " + df['レース名']

            c1, c2, c3 = st.columns(3)
            with c1:
                date_list = sorted(df['日付'].unique(), reverse=True)
                selected_date = st.selectbox("📅 開催日", date_list)
            with c2:
                venue_list = sorted(df[df['日付'] == selected_date]['開催場所'].unique())
                selected_venue = st.selectbox("📍 開催場所", venue_list)
            with c3:
                race_list = df[(df['日付'] == selected_date) & (df['開催場所'] == selected_venue)]['表示用レース名'].unique()
                selected_race = st.selectbox("🏁 レース", race_list)

            target_df = df[(df['表示用レース名'] == selected_race) & (df['開催場所'] == selected_venue) & (df['日付'] == selected_date)].sort_values("予想順位")

            if not target_df.empty:
                fig = px.bar(target_df, x='馬名', y='勝率', color='勝率', text_auto='.1f', color_continuous_scale='Greens', labels={'勝率':'期待勝率 (%)'})
                fig.update_layout(title_x=0.5) # グラフのタイトルも中央寄せ
                st.plotly_chart(fig, width='stretch')
                
                display_table = target_df[['予想順位', '馬番', '馬名', '勝率']].copy()
                display_table['勝率'] = display_table['勝率'].map('{:.1f}%'.format)
                display_table['馬番'] = display_table['馬番'].fillna('-').apply(lambda x: str(int(x)) if isinstance(x, float) else str(x))
                
                st.dataframe(display_table, hide_index=True, width='stretch')

# ③ レース特集（重賞予想など）
with tab3:
    st.markdown("<h2 style='text-align: center;'>🏆 今週の重賞特集</h2>", unsafe_allow_html=True)
    st.write("準備中：今週末の重賞レースに関するAIの見解を公開します。")

# ④ 会場データ
with tab4:
    st.markdown("<h2 style='text-align: center;'>📚 競馬場別・データ傾向分析</h2>", unsafe_allow_html=True)
    st.write("準備中：各競馬場別のAI解析による特注データを公開予定です。")

# ⑤ 競馬コラム
with tab5:
    st.markdown("<h2 style='text-align: center;'>📄 競馬AIタク・コラム</h2>", unsafe_allow_html=True)
    st.write("準備中：AI予測の仕組みや、期待値投資の重要性について綴ります。")
