import streamlit as st
import pandas as pd
import plotly.express as px
import glob
import io

st.set_page_config(page_title="競馬AIタク", layout="wide")
st.title("🏇 競馬AIタク 予測勝率")

# 全てのCSVファイルをリストアップ
files = glob.glob("*.csv")

if not files:
    st.write("CSVファイルを読み込み中です。しばらくお待ちください。")
else:
    df_list = []
    for f in files:
        try:
            # バイナリで読み込んでからPandasに渡す（これが一番安全）
            with open(f, 'rb') as b:
                data = b.read()
            # 日本語Excel形式(cp932)で読み込み
            tmp = pd.read_csv(io.BytesIO(data), encoding='cp932')
            df_list.append(tmp)
        except Exception as e:
            st.error(f"読み込み失敗: {f}")

    if df_list:
        df = pd.concat(df_list).drop_duplicates()
        
        # データの整理（日付などを選択肢に）
        date = st.selectbox("日付", df['日付'].unique())
        venue = st.selectbox("開催", df[df['日付']==date]['開催'].unique())
        race = st.selectbox("レース", df[(df['日付']==date) & (df['開催']==venue)]['レース名'].unique())
        
        target = df[(df['レース名']==race) & (df['開催']==venue)].sort_values("予想順位")
        
        # グラフ表示
        fig = px.bar(target, x='馬名', y='勝率', color='勝率', text_auto='.1f')
        st.plotly_chart(fig, use_container_width=True)
        
        # 表表示
        st.table(target[['予想順位', '馬番', '馬名', '勝率']])
