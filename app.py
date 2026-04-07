import streamlit as st
import pandas as pd
import plotly.express as px
import glob
import io

# ページの設定
st.set_page_config(page_title="競馬AIタク - 公式予測サイト", layout="wide")

st.title("🏇 競馬AIタク 予測勝率ダッシュボード")

menu = st.sidebar.selectbox("メニュー", ["各レースの予測勝率", "重賞コラム", "競馬コラム"])

if menu == "各レース의 予測勝率":
    st.header("📈 レース別 予測勝率")
    
    csv_files = glob.glob("*.csv")
    
    if not csv_files:
        st.warning("CSVファイルが見つかりません。")
    else:
        df_list = []
        for f in csv_files:
            try:
                # どんな文字コードでも対応できるようにバイナリ読み込みして判定
                with open(f, 'rb') as bfile:
                    raw_data = bfile.read()
                
                # cp932(日本語Windows)を最優先で試す設定
                df_tmp = pd.read_csv(io.BytesIO(raw_data), encoding='cp932')
                df_list.append(df_tmp)
            except Exception:
                try:
                    # ダメならUTF-8で試す
                    df_tmp = pd.read_csv(io.BytesIO(raw_data), encoding='utf-8')
                    df_list.append(df_tmp)
                except Exception as e:
                    st.error(f"ファイル {f} の読み込みエラー: {e}")

        if df_list:
            df = pd.concat(df_list).drop_duplicates()
            
            # 列名の空白などを除去（念のため）
            df.columns = df.columns.str.strip()
            
            # 選択メニュー
            date = st.selectbox("開催日を選択", sorted(df['日付'].unique(), reverse=True))
            venue = st.selectbox("開催場所を選択", df[df['日付']==date]['開催'].unique())
            race = st.selectbox("レースを選択", df[(df['日付']==date) & (df['開催']==venue)]['レース名'].unique())
            
            # 抽出
            target_df = df[(df['レース名']==race) & (df['開催']==venue)].sort_values("予想順位")
            
            # グラフ
            fig = px.bar(target_df, x='馬名', y='勝率', text='勝率', color='勝率', color_continuous_scale='Reds')
            st.plotly_chart(fig, use_container_width=True)
            
            # テーブル
            st.table(target_df[['予想順位', '馬番', '馬名', '勝率']])
else:
    st.write("コンテンツ準備中...")
