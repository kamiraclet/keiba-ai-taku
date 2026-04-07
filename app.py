import streamlit as st
import pandas as pd
import plotly.express as px
import glob
import io

st.set_page_config(page_title="競馬AIタク", layout="wide")
st.title("🏇 競馬AIタク 予測勝率")

# 1. フォルダ内のすべてのCSVファイルを探す
files = glob.glob("*.csv")

if not files:
    st.info("CSVファイルをGitHubにアップロードしてください。")
else:
    df_list = []
    for f in files:
        try:
            # バイナリモードで読み込み
            with open(f, 'rb') as b:
                data = b.read()
            # UTF-8で読み込みを試みる（ExcelでUTF-8保存した場合）
            tmp = pd.read_csv(io.BytesIO(data), encoding='utf-8')
            df_list.append(tmp)
        except Exception:
            try:
                # 失敗した場合はShift-JIS(cp932)で試みる
                tmp = pd.read_csv(io.BytesIO(data), encoding='cp932')
                df_list.append(tmp)
            except Exception as e:
                st.error(f"ファイル {f} の読み込みに失敗しました: {e}")

    if df_list:
        # すべてのCSVデータを1つに合体
        df = pd.concat(df_list).drop_duplicates()
        
        # 列名の余計な空白を削除
        df.columns = df.columns.str.strip()

        # --- UI部分 ---
        # 1. 日付を選択（最新の日付を一番上に）
        date_list = sorted(df['日付'].unique(), reverse=True)
        selected_date = st.selectbox("日付を選択", date_list)

        # 2. 開催場所を選択
        venue_list = df[df['日付'] == selected_date]['開催'].unique()
        selected_venue = st.selectbox("開催場所を選択", venue_list)

        # 3. レースを選択
        race_list = df[(df['日付'] == selected_date) & (df['開催'] == selected_venue)]['レース名'].unique()
        selected_race = st.selectbox("レースを選択", race_list)

        # --- データの表示 ---
        target_df = df[(df['レース名'] == selected_race) & (df['開催'] == selected_venue)].sort_values("予想順位")

        if not target_df.empty:
            # グラフ表示
            fig = px.bar(target_df, x='馬名', y='勝率', color='勝率', 
                         text_auto='.1f', color_continuous_scale='Reds',
                         labels={'勝率':'勝率 (%)'})
            st.plotly_chart(fig, use_container_width=True)
            
            # 表表示
            st.table(target_df[['予想順位', '馬番', '馬名', '勝率']])
