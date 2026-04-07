import streamlit as st
import pandas as pd
import plotly.express as px
import glob
import io

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
        st.warning("データファイル(CSV)が見つかりません。GitHubにCSVをアップロードしてください。")
    else:
        df_list = []
        for f in csv_files:
            # --- ここから文字コード自動判別ロジック ---
            with open(f, 'rb') as rawdata:
                bindata = rawdata.read()
            
            # 一般的なエンコーディングを順番に試す
            for enc in ['utf-8', 'cp932', 'shift_jis', 'euc-jp']:
                try:
                    df_tmp = pd.read_csv(io.BytesIO(bindata), encoding=enc)
                    df_list.append(df_tmp)
                    break 
                except:
                    continue
            # --- ここまで ---
            
        if not df_list:
            st.error("CSVファイルの読み込みに失敗しました。ファイル形式を確認してください。")
        else:
            df = pd.concat(df_list).drop_duplicates()
            
            # 日付選択
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

# 免責事項
st.markdown("---")
st.caption("※馬券の購入は自己責任でお願いします。本AIは的中を保証するものではありません。")
