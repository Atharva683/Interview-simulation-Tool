import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase Admin SDK with credentials directly
cred = credentials.Certificate({
    "type": "service_account",
  "project_id": "interview-9cc2a",
  "private_key_id": "73db5f26129dc00ed0d812d197ccfb0b52529d89",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCUevqAoopeq0aq\n4WJ/X6lUOjVhoZOysLJ60wgLijMjrikeqPX011Xbv5IRj4VrfQx3RB+Q2fsrKW5Z\nMa6G51zSORm5H4xvfmX11Xel8e4eUn3RjWJ5juERFoOf1VA4Pdv91YZNgF+3NlCp\nqvdnbvjuTYCC487cujMYLmdxTqwdmYgV6a2LECKszXbTS49/iru5iU0230mI+yoV\naA4kitX9vDtTOJ6m68DmrFA+p6uMEhNqXLZJPEaMDz98vlkd452yS4Dj2vR3s2Or\nOjV8T9dRO1VVkbInatpEsLkkPjp9CPCVyl8RezdTS6+u0NX/aAozldN1eKOO7bnr\nTIVI98L5AgMBAAECggEACpaYfYrZxjV9lRr8fKvUNeruupccor4CBEs/RB9nVTCK\nwyJ2Y67lcwW+w1zSPV+N/4VOoPRCeon6Ugb+dKVUE7O5t19eEudXGwhNf3p4qhXk\n3ggwkQ2U1DSgT0oVbeVPZlMPQECa0sRfTTIhcXFS9B93vh3Dty7aDOvmOYjMMlIQ\nJpkaXY3QHSKxmz24Jku6SRYhkh5kihAAe5QOmCECZINYl4hZrqlrJHpz3EzCCQXd\nFh7LgiA9KZcqbIikaxqfljAoBk1BaEtjGFA3NmTkyhQH60ePgZ6WIngd475WdjzX\nde4vpPBQThC5yMYKS1EHp4SU0xJdWxbs1X9noV7YWQKBgQDRoLmAYqowm5xsA8EG\nDRZt11wroktjDLPgJ5AmFw9W/iO64LLH+AsSEoaie3cFVWySUdPxfGz7LLUJ61Ei\n0gpkqz+OU7VABhCHD5f1uoOGkdViLGjuqdZNA2wgLEb2Q/PopaFhsyiSZFfRWXb8\nwd4RUXymmpHfOJWsJUGOkbl2xQKBgQC1U3WGp5ueJtbIstH41cyLoJXiKZKvxAi0\nIxydWqhNbI+0TOTral+joelZzZBTgyXlOpysUa9e/fDmWYXrSw1OIIEvlj1UY8nz\nfmStqTKL6ISnB/4vsUjdD9hruwObgYINusWeygtBrynG+JiJfjZ3Y03hFxdGoHEX\nTxvpAai+pQKBgGO9Q0WwrCVAhOZnytlkNL3CcBpat9/C1XrbmBxncGcFuF5cNvQq\nMqpAokqA0Bp7kJL12A/YEcpYdTLpAcu9gDBxwmWnsl9qA0cfxj+mpJnMnWh+lNap\nfEtcS3/rUUAvCMgytlxT8APnNllnZdPRMiWvTc2/UZSRybUEbPK2pzW5AoGBAIEL\niXuwcwbF21vwL5DpD25bdfAD6DogyJTy3B18dITNeyQ1CUIlbTU2OK1Jp6pXjrOp\n1/CnHaj8DuLQ2YcP3cM5TNdCFBmn/wTEcgBJhwidDTMWdCcbA6EX8s0Qxkt4iscc\noiIU5pfzgkbxixVm9npW+Qj1dwIzkuiky1czcBVlAoGBAMhAq4WdrI0LW3JyG8eg\nv1libqC/SSe9JiIdmDV/CFQda6Lk9yF6e/K3j5ssMX0kr0k8a+QGtbawNxNYTLmX\n/5heO4BH+5uvNlUY/c1/xf8F4iwe3OwOXqqHiVVcsAq/W6W5RnBe39cuUfPA8G0W\nQWA2IZTvAx5UgSlz6Fg1bYC2\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@interview-9cc2a.iam.gserviceaccount.com",
  "client_id": "104905277470582170878",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40interview-9cc2a.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
})
firebase_admin.initialize_app(cred)

def signup_user(email, password):
    """Create a new user with email and password."""
    try:
        user = auth.create_user(email=email, password=password)
        return {"success": True, "uid": user.uid}
    except Exception as e:
        return {"success": False, "error": str(e)}

def verify_token(id_token):
    """Verify Firebase ID Token."""
    try:
        decoded_token = auth.verify_id_token(id_token)
        return {"success": True, "uid": decoded_token["uid"]}
    except Exception as e:
        return {"success": False, "error": str(e)}
