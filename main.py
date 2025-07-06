from flask import Flask, render_template, request
import json
from datetime import datetime

app = Flask(__name__)

# Hàm tải file JSON
def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Hàm lưu file JSON
def save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Hàm lưu lịch sử trò chuyện
def save_history(user_input, bot_response):
    history = load_json('chat_history.json')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    history[timestamp] = {'user': user_input, 'bot': bot_response}
    save_json('chat_history.json', history)

# Hàm tìm câu trả lời dựa trên từ khóa
def find_response(user_input, responses):
    user_input = user_input.lower().strip()
    best_match = None
    max_matches = 0

    for response in responses:
        keywords = response['keywords']
        matches = sum(1 for keyword in keywords if keyword.lower() in user_input)
        if matches > max_matches:
            max_matches = matches
            best_match = response['answer']

    return best_match if best_match else "Xin lỗi, tôi không hiểu câu hỏi của bạn. Bạn có thể hỏi lại không?"

@app.route('/', methods=['GET', 'POST'])
def chatbot():
    responses = load_json('responses.json')
    history = load_json('chat_history.json')
    bot_response = "Chào bạn! Tôi là chatbot tư vấn của UMT. Hỏi tôi bất cứ điều gì về trường nhé!"

    user_input = None
    if request.method == 'POST':
        user_input = request.form.get('user_input', '').strip()
        if user_input.lower() in ['thoát', 'exit', 'bye']:
            bot_response = "Tạm biệt! Hẹn gặp lại!"
        else:
            bot_response = find_response(user_input, responses)
            save_history(user_input, bot_response)
        
        history = load_json('chat_history.json')

    sorted_history = sorted(history.items())

    return render_template('index.html', bot_response=bot_response, history=sorted_history, user_input=user_input)

if __name__ == '__main__':
    app.run(debug=True)