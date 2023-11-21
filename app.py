from flask import Flask, render_template, request, jsonify
import requests
import urllib3
import json
import base64

app = Flask(__name__)

openApiURL = "http://aiopen.etri.re.kr:8000/ObjectDetect"
accessKey = "cf4c0a24-df84-4af1-b896-ddc37f9d90e6"
naverClientId = "ziALS23mD4KX9OJX74GG"
naverClientSecret = "Ss9ydhFjrb"

# 네이버 API 설정
NAVER_CLIENT_ID = 'ziALS23mD4KX9OJX74GG'
NAVER_CLIENT_SECRET = 'Ss9ydhFjrb'

# 텍스트로 상품 정보 검색
def search_text(query):
    url = 'https://openapi.naver.com/v1/search/shop.json'
    headers = {
        'Content-Type': 'application/json',
        'X-Naver-Client-Id': NAVER_CLIENT_ID,
        'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
    }
    params = {'query': query, 'display': 20}
    
    response = requests.get(url, headers=headers, params=params)

    result = response.json()
    
    # 디버그를 위한 출력
    print("[Naver Response Code] " + str(response.status_code))
    print("[Naver Response Body]")
    print(result)
    
    # 응답 내용 확인 후 수정
    if 'items' in result:
        return result['items']
    else:
        return {'error': 'No items found in the response'}

# 이미지로 상품 검색
def search_image(image_file):
    image_contents = base64.b64encode(image_file.read()).decode("utf8")

    request_json = {
        "argument": {
            "type": "jpg",
            "file": image_contents
        }
    }

    http = urllib3.PoolManager()
    response = http.request(
        "POST",
        openApiURL,
        headers={"Content-Type": "application/json; charset=UTF-8", "Authorization": accessKey},
        body=json.dumps(request_json)
    )

    response_data = response.data.decode('utf-8')
    result = json.loads(response_data)

    if 'result' in result and result['result'] == 0:
        objects = result['return_object']['data']

        object_info = [{'label': obj['class'], 'confidence': obj['confidence']} for obj in objects]

        highest_confidence_obj = max(object_info, key=lambda x: x['confidence'])
        highest_confidence_category = highest_confidence_obj['label']

        naver_search_url = f"https://openapi.naver.com/v1/search/shop?query={highest_confidence_category}"
        headers = {
            'X-Naver-Client-Id': naverClientId,
            'X-Naver-Client-Secret': naverClientSecret
        }
        params = {'display': 20}
        naver_response = requests.get(naver_search_url, headers=headers, params=params)

        print("[Naver Response Code] " + str(naver_response.status_code))
        print("[Naver Response Body]")
        print(naver_response.text)

        if naver_response.status_code == 200:
            naver_result = naver_response.json()
            combined_result = {
                'objects': object_info,
                'highest_confidence_category': highest_confidence_category,
                'naver_result': naver_result['items']
            }
            return combined_result
        else:
            return {'error': 'Naver API Error'}
    else:
        return {'error': result.get('return_object', {}).get('data', 'Unknown Error')}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search_text', methods=['POST'])
def search_text_route():
    query = request.form.get('query')
    
    # 디버그를 위한 출력
    print("Received query:", query)

    text_results = search_text(query)
    
    return jsonify({'textResults': text_results})

@app.route('/search_image', methods=['POST'])
def search_image_route():
    image_file = request.files['image']

    image_results = search_image(image_file)

    return jsonify({'imageResults': image_results})

if __name__ == '__main__':
    # 외부에서 접속 가능한 모든 IP 주소, 포트 5000으로 설정
    app.run(host='0.0.0.0', port=5000, debug=True)
