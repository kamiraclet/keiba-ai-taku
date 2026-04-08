import streamlit as st
import pandas as pd
import plotly.express as px
import glob
import io
import re

# 1. ページの設定
st.set_page_config(page_title="競馬AIタク - 公式予測サイト", page_icon="🏇", layout="wide")

# デザインのカスタマイズ（右上のメニューやフッターを隠す）
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- サイドバー：プロフィール ＆ メニュー ---
st.sidebar.title("🏇 競馬AIタク")
st.sidebar.image("https://www.jp-p.jp/images/common/horse_icon.png") # 仮アイコン：後で自分のロゴに変更可能
st.sidebar.markdown("""
### プロフィール
30年分のレースデータと直近の馬場傾向を学習した独自AI。
感情を一切排し、**「期待値」のみ**を追求した予測勝率を算出します。
""")

menu = st.sidebar.radio(
    "メニューを選択",
    ["📊 レース別 予測勝率", "🏆 重賞予想コラム", "📚 レース会場データ考察", "📄 その他コラム"]
)

# --- メインコンテンツ ---

if menu == "📊 レース別 予測勝率":
    st.title("📈 各レースの予測勝率")
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
            except Exception as e:
                st.error(f"ファイル {f} の読み込みに失敗しました")

        if df_list:
            df = pd.concat(df_list).drop_duplicates()
            df.columns = df.columns.str.strip()
            df['開催場所'] = df['開催'].str.replace(r'\d+R$', '', regex=True)
            df['レース番号'] = df['開催'].str.extract(r'(\d+R)$')
            df['表示用レース名'] = df['レース番号'] + " " + df['レース名']

            # UI
            col1, col2, col3 = st.columns(3)
            with col1:
                date_list = sorted(df['日付'].unique(), reverse=True)
                selected_date = st.selectbox("日付を選択", date_list)
            with col2:
                venue_list = sorted(df[df['日付'] == selected_date]['開催場所'].unique())
                selected_venue = st.selectbox("開催場所を選択", venue_list)
            with col3:
                race_list = df[(df['日付'] == selected_date) & (df['開催場所'] == selected_venue)]['表示用レース名'].unique()
                selected_race = st.selectbox("レースを選択", race_list)

            target_df = df[(df['表示用レース名'] == selected_race) & (df['開催場所'] == selected_venue) & (df['日付'] == selected_date)].sort_values("予想順位")

            if not target_df.empty:
                fig = px.bar(target_df, x='馬名', y='勝率', color='勝率', text_auto='.1f', color_continuous_scale='Reds', labels={'勝率':'勝率 (%)'})
                st.plotly_chart(fig, width='stretch')
                
                display_table = target_df[['予想順位', '馬番', '馬名', '勝率']].copy()
                display_table['勝率'] = display_table['勝率'].map('{:.1f}%'.format)
                display_table['馬番'] = display_table['馬番'].fillna('-').apply(lambda x: str(int(x)) if isinstance(x, float) else str(x))
                
                st.dataframe(display_table, hide_index=True, width='stretch')

elif menu == "🏆 重賞予想コラム":
    st.title("🏆 重賞レース徹底分析")
    st.markdown("""
    ### 今週の注目：大阪杯 (G1)
    AIタクが導き出した今年の大阪杯のポイントは以下の3点です。
    1. **阪神芝2000mの適性**：内枠有利のデータが顕著。
    2. **上がり3Fの重要性**：過去5年の勝ち馬はすべて上がり3位以内。
    3. **AI推奨馬**：勝率25%を超えるアノ馬に注目。
    ---
    *ここに詳細な考察を書いていきます。*
    """)

elif menu == "📚 レース会場データ考察":
    st.title("📚 各開催場所のデータ考察")
    course = st.selectbox("競馬場を選択", ["中山競馬場", "東京競馬場", "阪神競馬場", "京都競馬場"])
    
    if course == "中山競馬場":
        st.subheader("中山競馬場の特徴")
        st.write("急坂があり、パワーとスタミナが要求されるタフなコースです。")
        # グラフや詳細データをここに追加可能

elif menu == "📄 その他コラム":
    st.title("📄 競馬コラム")
    st.write("競馬AIの仕組みや、期待値理論についての解説記事を掲載します。")
