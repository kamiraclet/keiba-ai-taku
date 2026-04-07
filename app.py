import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="競馬AIタク", layout="wide")
st.title("🏇 競馬AIタク 予測勝率")

# --- 動作確認用のサンプルデータ（ここを後でCSV化します） ---
data = {
    '日付': ['2026-04-05']*5,
    '開催': ['阪神']*5,
    'レース名': ['大阪杯']*5,
    '馬名': ['タスティエーラ', 'ローシャムパーク', 'ベラジオオペラ', 'プラダリア', 'ソールオリエンス'],
    '馬番': [1, 2, 3, 4, 5],
    '勝率': [15.5, 12.3, 25.4, 8.9, 10.2],
    '予想順位': [2, 3, 1, 5, 4]
}
df_sample = pd.DataFrame(data)

# --- 表示処理 ---
st.info("現在は動作確認用データを表示しています。")

# 選択メニュー
date = st.selectbox("日付", df_sample['日付'].unique())
venue = st.selectbox("開催", df_sample[df_sample['日付']==date]['開催'].unique())
race = st.selectbox("レース", df_sample[(df_sample['日付']==date) & (df_sample['開催']==venue)]['レース名'].unique())

target = df_sample[(df_sample['レース名']==race) & (df_sample['開催']==venue)].sort_values("予想順位")

# グラフ
fig = px.bar(target, x='馬名', y='勝率', color='勝率', text_auto='.1f', color_continuous_scale='Reds')
st.plotly_chart(fig, use_container_width=True)

# 表
st.table(target[['予想順位', '馬番', '馬名', '勝率']])

st.sidebar.markdown("### メニュー")
st.sidebar.write("・各レースの予測勝率 (公開中)")
st.sidebar.write("・重賞コラム (準備中)")
