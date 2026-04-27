import streamlit as st
from openai import OpenAI

# 1. ページ設定
st.set_page_config(page_title="Private Image Gen", page_icon="🎨")

# 2. Secretsから設定を読み込み
# Streamlit Cloudの「Advanced settings」 > 「Secrets」に設定した値を使用します
try:
    API_KEY = st.secrets["OPENAI_API_KEY"]
    APP_PASSWORD = st.secrets["MY_PASSWORD"]
except KeyError:
    st.error("Secretsの設定（OPENAI_API_KEY または MY_PASSWORD）が見つかりません。")
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
    prompt = st.text_area("プロンプト", placeholder="例: 桜が舞う現代の東京の街並み、アニメスタイル")
    
    col1, col2 = st.columns(2)
    with col1:
        quality = st.select_slider(
            "画質（コストに影響します）",
            options=["low", "standard", "hd"],
            value="standard"
        )
    with col2:
        size = st.selectbox(
            "サイズ",
            options=["1024x1024", "1024x1792", "1792x1024"],
            index=0
        )
    
    submit_button = st.form_submit_button("画像を生成する")

# 6. 生成実行
if submit_button:
    if not prompt:
        st.warning("プロンプトを入力してください。")
    else:
        with st.spinner("AIが画像を作成しています..."):
            try:
                # GPT Image 2.0 (DALL-E 3) 呼び出し
                response = client.images.generate(
                    model="gpt-image-2.0",
                    prompt=prompt,
                    n=1,
                    size=size,
                    quality=quality
                )
                
                image_url = response.data[0].url
                
                # 画像の表示
                st.divider()
                st.image(image_url, caption=f"Generated: {prompt[:30]}...")
                
                # ダウンロードボタンの提供
                st.markdown(f"[画像をブラウザで開く]({image_url})")
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

# 7. フッター
st.divider()
st.caption("※このアプリは従量課金APIを使用しています。使いすぎにご注意ください。")
