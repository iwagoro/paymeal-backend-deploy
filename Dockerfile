FROM python:3.12

# 作業ディレクトリを設定
WORKDIR /app

# 必要なファイルをコピー（requirements.txtのみ）
COPY ./requirements.txt /app/requirements.txt
COPY ./app /app

# パッケージのインストール
RUN pip install --upgrade pip && \
    pip install -r /app/requirements.txt

# ポートをエクスポート
EXPOSE 8080

# 環境変数を設定
ENV PYTHONUNBUFFERED True
ENV DB_HOST=aws-0-ap-northeast-1.pooler.supabase.com
ENV DB_NAME=postgres
ENV DB_PORT=6543
ENV DB_USER=postgres.uzgglkzvwvvrwqgtpxgj
ENV DB_PASSWORD=Breakinghartman733!
ENV API_KEY=a_fsmZNYh3RH_4HJR
ENV SECRET_KEY=wqU67SfaxjaILeEuJtpcrWzONLSB23Re9r7Vjhd6VPE=
ENV MERCHANT_ID=720008245077803008
ENV ADMIN_PASSWORD=Admin123


# エントリーポイントを設定
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]

