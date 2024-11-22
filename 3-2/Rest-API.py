""" 
REST-API 활용
회사 서버에서 KAKAO / GOOGLE OAuth 활용 로그인

"""
from flask import Flask, redirect, url_for, request, jsonify, session
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Google OAuth
GOOGLE_CLIENT_ID = '450413107026-84up3gk0p0lmcnl8pr6bbghave6phe2s.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '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t'
GOOGLE_REDIRECT_URI = 'http://localhost:5000/google/callback'

# Kakao OAuth
KAKAO_CLIENT_ID = 'your_kakao_client_id'
KAKAO_REDIRECT_URI = 'http://localhost:5000/kakao/callback'

@app.route('/')
def home():
    return "회사 메신저 로그인 시나리오"

# Google OAuth 시작
@app.route('/google/login')
def google_login():
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/auth"
        "?response_type=code"
        f"&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        "&scope=email profile"
    )
    return redirect(google_auth_url)

# Google OAuth 콜백
@app.route('/google/callback')
def google_callback():
    code = request.args.get('code')
    token_url = 'https://oauth2.googleapis.com/token'
    token_data = {
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code',
    }
    token_response = requests.post(token_url, data=token_data).json()
    access_token = token_response.get('access_token')

    user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
    user_info = requests.get(user_info_url, headers={'Authorization': f'Bearer {access_token}'}).json()

    session['google_user'] = user_info
    return jsonify(user_info)

# Kakao OAuth 시작
@app.route('/kakao/login')
def kakao_login():
    kakao_auth_url = (
        "https://kauth.kakao.com/oauth/authorize"
        "?response_type=code"
        f"&client_id={KAKAO_CLIENT_ID}"
        f"&redirect_uri={KAKAO_REDIRECT_URI}"
    )
    return redirect(kakao_auth_url)

# Kakao OAuth 콜백
@app.route('/kakao/callback')
def kakao_callback():
    code = request.args.get('code')
    token_url = 'https://kauth.kakao.com/oauth/token'
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': KAKAO_CLIENT_ID,
        'redirect_uri': KAKAO_REDIRECT_URI,
        'code': code,
    }
    token_response = requests.post(token_url, data=token_data).json()
    access_token = token_response.get('access_token')

    user_info_url = 'https://kapi.kakao.com/v2/user/me'
    user_info = requests.get(user_info_url, headers={'Authorization': f'Bearer {access_token}'}).json()

    session['kakao_user'] = user_info
    return jsonify(user_info)

# 통합 연동
@app.route('/integrate')
def integrate():
    google_user = session.get('google_user')
    kakao_user = session.get('kakao_user')

    if not google_user or not kakao_user:
        return "Google 및 Kakao 계정 연동이 필요합니다.", 400

    integration_result = {
        "google": google_user,
        "kakao": kakao_user,
        "status": "Accounts integrated successfully!"
    }
    return jsonify(integration_result)

if __name__ == '__main__':
    app.run(debug=True)
