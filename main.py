import streamlit as st
from openai import OpenAI
import os

# 1. サイドバーで設定（APIキーを環境変数から取得）
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("GPT Image 2.0 Generator")
st.caption("従量課金APIを利用した画像生成ツール")

# 2. 入力フォーム
prompt = st.text_area("生成したい画像のプロンプトを入力してください", placeholder="例：富士山をバックに走るサイバーパンクなバイク")

if st.button("画像を生成"):
    if not prompt:
        st.warning("プロンプトを入力してください")
    else:
        with st.spinner("AIが画像を生成中..."):
            try:
                # 画像生成リクエスト
                response = client.images.generate(
                    model="gpt-image-2.0",
                    prompt=prompt,
                    size="1024x1024",
                    quality="standard"
                )
                
                # 結果の表示
                image_url = response.data[0].url
                st.image(image_url, caption="生成された画像")
                st.success("生成完了！")
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
