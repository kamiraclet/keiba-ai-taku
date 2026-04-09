import streamlit as st
import pandas as pd
import plotly.express as px
import glob
import io
import re

# 1. SEO設定
st.set_page_config(
    page_title="競馬AIタク | データサイエンスが導く予測勝率と期待値の最終結論", 
    page_icon="🏇", 
    layout="wide"
)

# --- カスタムCSS ---
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

    .stTabs [data-baseweb="tab-list"] {
        display: flex;
        justify-content: center;
        gap: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #006400 !important;
        color: white !important;
    }
    
    /* フッターデザイン */
    .custom-footer {
        margin-top: 5rem;
        padding: 2rem 0;
        border-top: 1px solid #eee;
        text-align: center;
        color: #999;
        font-size: 0.8rem;
    }
</style>
"""
st.markdown(style, unsafe_allow_html=True)

# --- クエリパラメータによるページ制御（フッターリンク用） ---
# URLの末尾に ?page=policy が付いているかチェック
query_params = st.query_params
show_policy = query_params.get("page") == "policy"

# --- サイトヘッダー ---
st.markdown(f"""
<div class="title-container">
    <h1 style='font-size: 3rem; color: #1a3321; margin-bottom: 0;'>🏇 競馬AIタク</h1>
    <p style='font-size: 1.2rem; color: #444; font-weight: bold; margin-top: 10px;'>
        〜 30年分のビッグデータが導く「勝つための期待値」を全レース無料公開 〜
    </p>
</div>
""", unsafe_allow_html=True)

if show_policy:
    # --- プライバシーポリシー専用画面 ---
    st.markdown("<h2 style='text-align: center;'>⚖️ プライバシーポリシー & 免責事項</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background: #f9f9f9; padding: 30px; border-radius: 10px; line-height: 1.8; color: #333;">
        <b>1. 広告の配信について</b><br>
        当サイトでは、第三者配信の広告サービス（Googleアドセンス等）を利用することがあります。広告配信事業者は、ユーザーの興味に応じた広告を表示するため、クッキー（Cookie）を使用することがあります。<br><br>
        <b>2. 免責事項</b><br>
        本サイトに掲載されている予測データはAIによる算出結果であり、的中を保証するものではありません。馬券の購入は必ずご自身の責任において行ってください。本サイトの情報を利用したことによる損害について、当方は一切の責任を負いません。
    </div>
    <br>
    <div style='text-align: center;'><a href='/' target='_self'>← サイトへ戻る</a></div>
    """, unsafe_allow_html=True)

else:
    # --- 通常のメインコンテンツ（タブ） ---
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "👤 開発者紹介", "🤖 競馬AIについて", "📊 予測勝率公開", "🏆 レース特集", "📚 会場データ", "📄 競馬コラム"
    ])

    with tab1:
        st.markdown("<h2 style='text-align: center;'>AI予想家タク プロフィール</h2>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center;'><img src='https://www.jp-p.jp/images/common/horse_icon.png' width='100'></div>", unsafe_allow_html=True)
        st.write("netkeibaやX、note等で活動。データサイエンスに基づいた期待値投資を提唱。")

    with tab2:
        st.markdown("<h2 style='text-align: center;'>🤖 競馬AIタクのロジック</h2>", unsafe_allow_html=True)
        st.write("深層学習モデルを用い、馬場差・風速等を補正した予測勝率を算出。")

    with tab3:
        st.markdown("<h2 style='text-align: center;'>📈 最新レース予測勝率</h2>", unsafe_allow_html=True)
        files = glob.glob("*.csv")
        if not files:
            st.info("解析データ準備中...")
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
                df['開催場所'] = df['開催'].astype(str).str.replace(r'\d+R$', '', regex=True)
                race_num = df['開催'].astype(str).str.extract(r'(\d+R)$')[0].fillna('')
                df['表示用レース名'] = race_num + " " + df['レース名'].astype(str)

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

    with tab4: st.write("### 🏆 重賞レース特集（準備中）")
    with tab5: st.write("### 📚 会場データ考察（準備中）")
    with tab6: st.write("### 📄 競馬コラム（準備中）")

# --- フッター ---
# ここにプライバシーポリシーのリンクを設置
st.markdown(f"""
<div class="custom-footer">
    <p>© 2026 競馬AIタク All Rights Reserved.</p>
    <p><a href="/?page=policy" target="_self" style="color: #999; text-decoration: none;">プライバシーポリシー・免責事項</a></p>
</div>
""", unsafe_allow_html=True)
