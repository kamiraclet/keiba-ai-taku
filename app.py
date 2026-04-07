import streamlit as st
import pandas as pd
import plotly.express as px
import glob
import io
import re

# ページの設定
st.set_page_config(page_title="競馬AIタク - 公式予測サイト", page_icon="🏇", layout="wide")

# --- デザインのカスタマイズ（右上のメニューやフッターを隠す） ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

st.title("🏇 競馬AIタク 予測勝率")

# 1. フォルダ内のすべてのCSVファイルを探す
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

        # --- データ加工 ---
        df['開催場所'] = df['開催'].str.replace(r'\d+R$', '', regex=True)
        df['レース番号'] = df['開催'].str.extract(r'(\d+R)$')
        df['表示用レース名'] = df['レース番号'] + " " + df['レース名']

        # --- UI部分 ---
        date_list = sorted(df['日付'].unique(), reverse=True)
        selected_date = st.selectbox("日付を選択", date_list)

        venue_list = sorted(df[df['日付'] == selected_date]['開催場所'].unique())
        selected_venue = st.selectbox("開催場所を選択", venue_list)

        race_list = df[(df['日付'] == selected_date) & (df['開催場所'] == selected_venue)]['表示用レース名'].unique()
        selected_race = st.selectbox("レースを選択", race_list)

        # --- データの抽出と表示 ---
        target_df = df[(df['表示用レース名'] == selected_race) & (df['開催場所'] == selected_venue) & (df['日付'] == selected_date)].sort_values("予想順位")

        if not target_df.empty:
            # グラフ表示
            fig = px.bar(target_df, x='馬名', y='勝率', color='勝率', 
                         text_auto='.1f', color_continuous_scale='Reds',
                         labels={'勝率':'勝率 (%)'})
            st.plotly_chart(fig, use_container_width=True)
            
            # --- 表の表示（修正箇所） ---
            display_table = target_df[['予想順位', '馬番', '馬名', '勝率']].copy()
            
            # 1. 勝率を少数第一位までにして、単位に%をつける
            display_table['勝率'] = display_table['勝率'].map('{:.1f}%'.format)
            
            # 2. 馬番が空(NaN)の場合に備えて整数表示にする（データがある場合のみ）
            display_table['馬番'] = display_table['馬番'].fillna('-')
            
            #
