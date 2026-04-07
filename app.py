import streamlit as st
import pandas as pd
import plotly.express as px
import glob
import os

# ページの設定
st.set_page_config(page_title="競馬AIタク - 公式予測サイト", layout="wide")

# タイトル
st.title("🏇 競馬AIタク 予測勝率ダッシュボード")

# サイドメニュー
menu = st.sidebar.selectbox("メニュー", ["各レースの予測勝率", "重賞コラム", "競馬コラム", "競馬場データ考察"])

if menu == "各レースの予測勝率":
    st.header("📈 レース別 予測勝率")
    
    # CSVファイルの読み込み
    csv_files = glob.glob("*.csv")
    if not csv_files:
        st.warning("データファイル(CSV)が見つかりません。")
    else:
        # 日付選択（CSVファイル名から取得、またはデータ内から取得）
        # 今回はシンプルにアップロードされている全CSVを統合
        df_list = []
        for f in csv_files:
            try:
                # まずは標準のUTF-8で試す
                df_list.append(pd.read_csv(f))
            except UnicodeDecodeError:
                # ダメならShift-JISで試す（Excelで作ったCSVはこっちが多い）
                df_list.append(pd.read_csv(f, encoding='cp932'))
        df = pd.concat(df_list).drop_duplicates()
        
        # 選択UI
        dates = sorted(df['日付'].unique(), reverse=True)
        selected_date = st.selectbox("開催日を選択", dates)
        
        venues = df[df['日付'] == selected_date]['開催'].unique()
        selected_venue = st.selectbox("開催場所を選択", venues)
        
        races = df[(df['日付'] == selected_date) & (df['開催'] == selected_venue)]['レース名'].unique()
        selected_race = st.selectbox("レースを選択", races)
        
        # データの抽出
        display_df = df[(df['レース名'] == selected_race) & (df['開催'] == selected_venue)].sort_values("予想順位")
        
        # グラフ作成
        fig = px.bar(display_df, x='馬名', y='勝率', text='勝率', color='勝率',
                     color_continuous_scale='Reds', labels={'勝率':'勝率(%)'})
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
        
        # 表の表示
        st.dataframe(display_df[['予想順位', '馬番', '馬名', '勝率']].set_index('予想順位'), use_container_width=True)

else:
    st.subheader(f"【{menu}】")
    st.write("現在、記事を準備中です。タクがデータを分析しています。")

# 免責事項（全ページ共通で下部に表示）
st.markdown("---")
st.caption("※馬券の購入は自己責任でお願いします。本AIは的中を保証するものではありません。")
