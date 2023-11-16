from flask import Flask, request, jsonify, render_template
import requests
import json

# Flask 클래스의 인스턴스인 app을 생성
app = Flask(__name__)

# 루트 URL('/')에 대한 라우팅을 설정합니다. 이 URL로 요청이 오면 index 함수가 호출
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search')
def search():
    query = request.args.get('query')

    # 네이버 OpenAPI를 호출
    headers = {
        'Content-Type': 'plain/text',
        'X-Naver-Client-Id': 'ziALS23mD4KX9OJX74GG',
        'X-Naver-Client-Secret': 'Ss9ydhFjrb'
    }
    # 네이버 OpenAPI를 호출할 때 사용할 쿼리 파라미터를 설정 query -> shop, display -> 검색 개수
    params = {'query': query, 'display': 10}
    
    # requests.get 함수를 사용하여 네이버 OpenAPI를 호출하고, 그 결과를 response 변수에 저장
    response = requests.get('https://openapi.naver.com/v1/search/shop', headers=headers, params=params)

    # HTTP 응답 코드가 200(성공)인 경우, 응답 바디를 JSON으로 파싱하고 그 중 'items' 부분만 클라이언트에 반환
    if response.status_code == 200:
        return jsonify(response.json()['items'])
    else:
        return jsonify(response.json())

# 서버 실행
if __name__ == '__main__':
    app.run(port=3000)
