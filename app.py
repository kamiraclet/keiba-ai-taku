import streamlit as st
import pandas as pd
import plotly.express as px
import glob
import io
import re

# 1. ページの設定
st.set_page_config(page_title="競馬AIタク - 公式予測サイト", page_icon="🏇", layout="wide")

# デザインのカスタマイズ（右上のメニューやフッター、余計な余白を消す）
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            /* 上部の余白を詰める */
            .block-container {padding-top: 2rem;}
            /* タブの文字を大きくする */
            button[data-baseweb="tab"] {font-size: 18px; font-weight: bold;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- サイトロゴとタイトル ---
col_logo, col_title = st.columns([1, 8])
with col_logo:
    st.image("https://www.jp-p.jp/images/common/horse_icon.png", width=80) # 自作ロゴがあれば差し替え
with col_title:
    st.title("競馬AIタク - データ予測プラットフォーム")

# --- 上部ナビゲーションメニュー（タブ） ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 予測勝率", 
    "🏆 重賞予想", 
    "📚 会場データ考察", 
    "📄 競馬コラム", 
    "👤 プロフィール"
])

# --- 各メニューの内容 ---

# ① 予測勝率
with tab1:
    st.header("📈 レース別 予測勝率")
    files = glob.glob("*.csv")

    if not files:
        st.info("CSVファイルをGitHubにアップロードしてください。")
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

            # 横並びのセレクター
            c1, c2, c3 = st.columns(3)
            with c1:
                date_list = sorted(df['日付'].unique(), reverse=True)
                selected_date = st.selectbox("日付", date_list)
            with c2:
                venue_list = sorted(df[df['日付'] == selected_date]['開催場所'].unique())
                selected_venue = st.selectbox("開催場所", venue_list)
            with c3:
                race_list = df[(df['日付'] == selected_date) & (df['開催場所'] == selected_venue)]['表示用レース名'].unique()
                selected_race = st.selectbox("レース", race_list)

            target_df = df[(df['表示用レース名'] == selected_race) & (df['開催場所'] == selected_venue) & (df['日付'] == selected_date)].sort_values("予想順位")

            if not target_df.empty:
                fig = px.bar(target_df, x='馬名', y='勝率', color='勝率', text_auto='.1f', color_continuous_scale='Reds', labels={'勝率':'勝率 (%)'})
                st.plotly_chart(fig, width='stretch')
                
                display_table = target_df[['予想順位', '馬番', '馬名', '勝率']].copy()
                display_table['勝率'] = display_table['勝率'].map('{:.1f}%'.format)
                display_table['馬番'] = display_table['馬番'].fillna('-').apply(lambda x: str(int(x)) if isinstance(x, float) else str(x))
                
                st.dataframe(display_table, hide_index=True, width='stretch')

# ② 重賞予想
with tab2:
    st.header("🏆 重賞レース徹底分析")
    st.subheader("今週の注目：大阪杯 (G1)")
    st.write("ここに重賞の考察記事を書いていきます。")

# ③ 会場データ考察
with tab3:
    st.header("📚 各開催場所のデータ考察")
    course = st.radio("競馬場を選択", ["中山", "東京", "阪神", "京都"], horizontal=True)
    st.write(f"### {course}競馬場の傾向分析")
    st.write("コースの特徴や有利な脚質などのデータを記載します。")

# ④ 競馬コラム
with tab4:
    st.header("📄 競馬コラム")
    st.write("AI予想の裏側や馬券術についての読み物です。")

# ⑤ プロフィール
with tab5:
    st.header("👤 プロフィール")
    col_p1, col_p2 = st.columns([1, 3])
    with col_p1:
        st.image("https://www.jp-p.jp/images/common/horse_icon.png")
    with col_p2:
        st.write("""
        **名前：競馬AIタク**
        
        30年分のレースデータと直近の馬場傾向を学習した独自AI。
        感情を一切排し、**「期待値」のみ**を追求した予測勝率を算出します。
        知名度と権威性を高め、皆様の競馬ライフに貢献することを目指しています。
        """)
