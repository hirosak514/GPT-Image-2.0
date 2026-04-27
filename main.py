import streamlit as st
from openai import OpenAI
import base64

# 1. ページ設定
st.set_page_config(page_title="Private Image Gen", page_icon="🎨")

# 2. Secretsから設定を読み込み
try:
    API_KEY = st.secrets["OPENAI_API_KEY"]
    APP_PASSWORD = st.secrets["MY_PASSWORD"]
except KeyError:
    st.error("StreamlitのSecrets設定が見つかりません。")
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

# 5. 画像をBase64にエンコードする関数
def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

# 6. メイン画面のUI
st.title("🎨 GPT Image 2.0 Generator")
st.write("参照画像やプロンプトを元に画像を生成します（従量課金）")

with st.form("gen_form"):
    # 参照画像のアップロード
    uploaded_file = st.file_uploader("参照画像をアップロード（任意）", type=["png", "jpg", "jpeg"])
    
    if uploaded_file:
        st.image(uploaded_file, caption="アップロードされた参照画像", width=200)

    prompt = st.text_area("追加のプロンプト・指示", placeholder="例: スタンドマイクで歌っている。アニメスタイルで。")
    
    col1, col2 = st.columns(2)
    with col1:
        quality = st.select_slider(
            "画質",
            options=["standard", "hd"],
            value="standard"
        )
    with col2:
        size_option = st.selectbox(
            "出力サイズ",
            options=[
                "正方形 (1024x1024)", 
                "スマホ縦画面 (1024x1792)", 
                "YouTube横画面 (1792x1024)"
            ],
            index=0
        )
        
        if "正方形" in size_option:
            size = "1024x1024"
        elif "スマホ縦画面" in size_option:
            size = "1024x1792"
        else:
            size = "1792x1024"
    
    submit_button = st.form_submit_button("画像を生成する")

# 7. 生成実行
if submit_button:
    if not prompt and not uploaded_file:
        st.warning("プロンプトを入力するか、画像をアップロードしてください。")
    else:
        with st.spinner("AIが内容を分析・生成しています..."):
            try:
                final_prompt = prompt
                
                # 画像がある場合、Vision APIで「ポリシーに安全なプロンプト」へ変換
                if uploaded_file:
                    base64_image = encode_image(uploaded_file)
                    vision_response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text", 
                                        "text": (
                                            "Convert this image into a detailed descriptive English prompt for DALL-E 3. "
                                            "CRITICAL SAFETY RULE: Do not mention any names of real people, celebrities, or specific copyrighted characters. "
                                            "Instead, describe their appearance (e.g., hair style, clothing, age, gender) in generic terms. "
                                            f"Also, incorporate the following user's modification request: {prompt}"
                                        )
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                                    },
                                ],
                            }
                        ],
                        max_tokens=500,
                    )
                    final_prompt = vision_response.choices[0].message.content

                # DALL-E 3 で画像生成
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=final_prompt,
                    n=1,
                    size=size,
                    quality=quality,
                    response_format="url"
                )
                
                image_url = response.data[0].url
                
                st.divider()
                st.image(image_url, caption="生成された画像")
                st.markdown(f"🔗 [フルサイズ画像をブラウザで開く]({image_url})")
                
            except Exception as e:
                # ポリシーエラーの場合、より分かりやすい警告を表示
                if "content_policy_violation" in str(e):
                    st.error("セーフティフィルターにより生成が拒否されました。実在の人物に似すぎているか、不適切な表現が含まれている可能性があります。指示を少し変えてみてください。")
                else:
                    st.error(f"エラーが発生しました: {e}")

# 8. フッター
st.divider()
st.caption("※参照画像の解析（Vision API）と画像生成（DALL-E 3）の両方でトークンを消費します。")
