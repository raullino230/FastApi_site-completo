import requests

headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3IiwiZXhwIjoxNzg5MDY3MDIzfQ.xNHEWXIRFG87pkI37quJDD3hfiZvozDfxeoGCVZ3oco"
}

requisição =requests.get("http://127.0.0.1:8000/auth/refresh", headers = headers)

print(requisição)
print(requisição.json)