import streamlit as st
import pandas as pd
import plotly.express as px
import glob
import io
import re

# 1. SEOを意識したページ設定
st.set_page_config(
    page_title="競馬AIタク | データサイエンスが導く予測勝率と期待値の最終結論", 
    page_icon="🏇", 
    layout="wide"
)

# --- カスタムCSS（デザイン調整） ---
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

    /* タブメニューの中央寄せ */
    .stTabs [data-baseweb="tab-list"] {
        display: flex;
        justify-content: center;
        gap: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #006400 !important;
        color: white !important;
    }
    
    /* フッターのデザイン */
    .custom-footer {
        margin-top: 5rem;
        padding: 2rem;
        border-top: 1px solid #eee;
        text-align: center;
        color: #888;
        font-size: 0.8rem;
    }
</style>
"""
st.markdown(style, unsafe_allow_html=True)

# --- サイトヘッダー ---
st.markdown("""
<div class="title-container">
    <h1 style='font-size: 3rem; color: #1a3321; margin-bottom: 0;'>🏇 競馬AIタク</h1>
    <p style='font-size: 1.2rem; color: #444; font-weight: bold; margin-top: 10px;'>
        〜 30年分のビッグデータが導く「勝つための期待値」を全レース無料公開 〜
    </p>
</div>
""", unsafe_allow_html=True)

# --- メインメニュー（タブ） ---
# 「ポリシー」を削除し、コンテンツに特化させました
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "👤 開発者紹介", 
    "🤖 競馬AIについて",
    "📊 予測勝率公開", 
    "🏆 レース特集", 
    "📚 会場データ", 
    "📄 競馬コラム"
])

# --- 各メニューの内容 ---

with tab1:
    col_p1, col_p2, col_p3 = st.columns([1, 2, 1])
    with col_p2:
        st.markdown("<h2 style='text-align: center;'>AI予想家タク プロフィール</h2>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center;'>
