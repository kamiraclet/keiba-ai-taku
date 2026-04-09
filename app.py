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
        padding-top: 1rem;
        margin: auto;
    }

    .title-container {
        text-align: center;
        padding-bottom: 1rem;
    }

    /* ヘッダー画像の設定 */
    .header-img {
        width: 100%;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    .stTabs [data-baseweb="tab-list"] {
        display: flex;
        justify-content: center;
        gap: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #006400 !important;
        color: white !important;
    }
    
    /* プライバシーポリシー用 */
    .policy-box {
        font-size: 0.8rem;
        color: #666;
        background: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
    }
</style>
"""
st.markdown(style, unsafe_allow_html=True)

# --- ヘッダー画像とタイトル ---
# ※画像URLは後述の「画像生成」で作成したものをここに貼る想定です
st.markdown("""
<div class="title-container">
    <img src="https://images.unsplash.com/photo-1599202860130-f600f4948364?q=80&w=1000&auto=format&fit=crop" class="header-img" alt="競馬AIイメージ">
    <h1 style='font-size: 2.5rem;'>🏇 競馬AIタク</h1>
    <p style='font-size: 1.1rem; color: #666;'>〜 30年分のビッグデータが導く「勝つための期待値」を全レース無料公開 〜</p>
</div>
""", unsafe_allow_html=True)

# --- メニュー（タブ） ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "👤 開発者紹介", 
    "🤖 競馬AIについて",
    "📊 予測勝率公開", 
    "🏆 レース特集", 
    "📚 会場データ", 
    "📄 競馬コラム",
    "⚖️ ポリシー"
])

# --- 各メニューの内容 ---

with tab1:
    col_p1, col_p2, col_p3 = st.columns([1, 2, 1])
    with col_p2:
        st.markdown("<h2 style='text-align: center;'>AI予想家タク プロフィール</h2>", unsafe_allow_html=True)
        st.write("""
        **【データと理論を融合させた真実の追求】**
        
        netkeibaやX(旧Twitter)、note等のプラットフォームで活動するデータサイエンティスト。
        幼少期より競馬の血統理論と統計学に魅了され、独自に予想モデルを構築。
        
        **■ 活動方針**
        「競馬は記憶ではなく記録のスポーツである」を信条とし、パドックの主観や感情を排除。
        的中率よりも「長期的な回収率（期待値）」を最大化させるための数値を公開しています。
        
        **■ 配信実績**
        - **note**: 重賞レースの期待値解析レポートを毎週配信
        - **BOOKERS**: 独自の「タク指数」に基づいた全レース買い目を公開
        - **X**: リアルタイムの馬場傾向変化をAIが解析して速報
        """)

with tab2:
    st.markdown("<h2 style='text-align: center;'>🤖 競馬AIタクのロジック</h2>", unsafe_allow_html=True)
    st.write("""
    **「
