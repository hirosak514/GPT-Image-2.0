import streamlit as st
from openai import OpenAI

# 1. ページ設定
st.set_page_config(page_title="Private Image Gen", page_icon="🎨")

# 2. Secretsから設定を読み込み
try:
    API_KEY = st.secrets["OPENAI_API_KEY"]
    APP_PASSWORD = st.secrets["MY_PASSWORD"]
except KeyError:
    st.error("StreamlitのSecrets設定（OPENAI_API_KEY または MY_PASSWORD）が見つかりません。")
    st.stop()

# 3. サイドバーで認証
st.sidebar.title("🔒 Authentication")
user_password = st.sidebar.text_input("パスワードを入力してください", type="password")

if not user_password:
    st.info("サイドバーからパスワードを入力してログインしてください。")
    st.stop()

if user_password != APP_PASSWORD:
    st.sidebar.error("パスワードが正しくありません。")
    st.stop()

st.sidebar.success("認証済み")

# 4. APIクライアントの初期化
client = OpenAI(api_key=API_KEY)

# 5. メイン画面のUI
st.title("🎨 GPT Image 2.0 Generator")
st.write("プロンプトを入力して画像を生成します（従量課金）")

with st.form("gen_form"):
    prompt = st.text_area("プロンプト", placeholder="例: アフロヘアの男性ファンク歌手がステージで歌っている。")
    
    col1, col2 = st.columns(2)
    with col1:
        # 従量課金コストを抑えたい場合は 'standard'、高品質なら 'hd'
        quality = st.select_slider(
            "画質（コストに影響します）",
            options=["standard", "hd"],
            value="standard"
        )
    with col2:
        # 出力サイズの選択肢を日本語で分かりやすく追加
        size_option = st.selectbox(
            "出力サイズ",
            options=[
                "正方形 (1024x1024)", 
                "スマホ縦画面 (1024x1792)", 
                "YouTube横画面 (1792x1024)"
            ],
            index=0
        )
        
        # APIに渡す形式に変換
        if "正方形" in size_option:
            size = "1024x1024"
        elif "スマホ縦画面" in size_option:
            size = "1024x1792"
        else:
            size = "1792x1024"
    
    submit_button = st.form_submit_button("画像を生成する")

# 6. 生成実行
if submit_button:
    if not prompt:
        st.warning("プロンプトを入力してください。")
    else:
        with st.spinner("AIが画像を作成しています..."):
            try:
                # モデル名を 'dall-e-3' に修正
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    n=1,
                    size=size,
                    quality=quality,
                    response_format="url"
                )
                
                image_url = response.data[0].url
                
                # 画像の表示
                st.divider()
                st.image(image_url, caption=f"生成された画像 ({size_option})")
                
                # ダウンロードリンク
                st.markdown(f"🔗 [フルサイズ画像をブラウザで開く]({image_url})")
                
            except Exception as e:
                # 残高不足やポリシー違反などのエラー内容を表示
                st.error(f"エラーが発生しました: {e}")

# 7. フッター
st.divider()
st.caption("※このアプリは従量課金APIを使用しています。OpenAIの管理画面で利用額を定期的に確認してください。")
