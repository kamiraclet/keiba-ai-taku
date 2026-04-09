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
        padding-top: 2rem; /* 画像を消した分、少しだけ上に余裕を持たせる */
        margin: auto;
    }

    .title-container {
        text-align: center;
        padding-bottom: 2rem;
        border-bottom: 2px solid #f0f2f6; /* 境界線を入れて引き締める */
        margin-bottom: 2rem;
    }

    .stTabs [data-baseweb="tab-list"] {
        display: flex;
        justify-content: center;
        gap: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #006400 !important;
        color: white !important;
    }
    
    .policy-box {
        font-size: 0.8rem;
        color: #666;
        background: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
        line-height: 1.6;
    }
</style>
"""
st.markdown(style, unsafe_allow_html=True)

# --- サイトヘッダー（画像なし・テキストのみ） ---
st.markdown("""
<div class="title-container">
    <h1 style='font-size: 3rem; color: #1a3321; margin-bottom: 0;'>🏇 競馬AIタク</h1>
    <p style='font-size: 1.2rem; color: #444; font-weight: bold; margin-top: 10px;'>
        〜 30年分のビッグデータが導く「勝つための期待値」を全レース無料公開 〜
    </p>
</div>
""", unsafe_allow_html=True)

# --- メニュー（タブ） ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "👤 開発者紹介", 
    "🤖 競馬AIについて",
    "📊 予測勝率公開", 
    "🏆 レース特集", 
    "📚 会場データ", 
    "📄 競馬コラム",
    "⚖️ ポリシー"
])

# --- 各メニューの内容 ---

with tab1:
    col_p1, col_p2, col_p3 = st.columns([1, 2, 1])
    with col_p2:
        st.markdown("<h2 style='text-align: center;'>AI予想家タク プロフィール</h2>", unsafe_allow_html=True)
        # 画像がないと寂しい場合は、小さなアイコンだけ残すと権威性が出ます
        st.markdown("<div style='text-align: center;'><img src='https://www.jp-p.jp/images/common/horse_icon.png' width='100'></div>", unsafe_allow_html=True)
        st.write("""
        **【データと理論を融合させた真実の追求】**
        
        netkeibaやX(旧Twitter)、note等のプラットフォームで活動するデータサイエンティスト。
        幼少期より競馬の血統理論と統計学に魅了され、独自に予想モデルを構築。
        
        **■ 活動方針**
        「競馬は記憶ではなく記録のスポーツである」を信条とし、パドックの主観や感情を排除。
        的中率よりも「長期的な回収率（期待値）」を最大化させるための数値を公開しています。
        
        **■ 配信実績**
        - **note**: 重賞レースの期待値解析レポートを毎週配信
        - **BOOKERS**: 独自の「タク指数」に基づいた全レース買い目を公開
        - **X**: リアルタイムの馬場傾向変化をAIが解析して速報
        """)

with tab2:
    st.markdown("<h2 style='text-align: center;'>🤖 競馬AIタクのロジック</h2>", unsafe_allow_html=True)
    st.write("""
    **「競馬AIタク」は、単なる過去データの集計機ではありません。**
    
    独自に開発した深層学習（Deep Learning）モデルを用い、多角的に解析。
    当日の馬場差、風速、含水率によるタイム補正に加え、各馬の走法と会場の相性を数値化しています。
    
    このAIが導き出す「予測勝率」は、皆様が馬券を組み立てる際の最強の武器となります。
    """)

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
            df['レース番号'] = df['開催'].str.extract(r'(\d+R)$')
            df['表示用レース名'] = df['レース番号'] + " " + df['レース名']

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
    st.write("準備中：AI予測の仕組みや、期待値投資の重要性について綴ります。")

with tab7:
    st.markdown("### プライバシーポリシー")
    st.markdown("""
    <div class="policy-box">
    当サイト（以下、本サイト）は、ユーザーの個人情報保護を重視しています。
    <br><br>
    <b>1. 広告の配信について</b><br>
    本サイトでは、第三者配信の広告サービス（Googleアドセンス等）を利用することがあります。クッキー（Cookie）を使用することがあります。
    <br><br>
    <b>2. 免責事項</b><br>
    本サイトに掲載されている予測データはAIによる算出結果であり、的中を保証するものではありません。馬券の購入は必ずご自身の責任において行ってください。本サイトの情報を利用したことによる損害について、当方は一切の責任を負いません。
    </div>
    """, unsafe_allow_html=True)
