from flask import Flask, request, jsonify
from flask_cors import CORS  # 用于处理跨域请求 / For handling cross-origin requests
import mysql.connector  # 用于连接 MySQL 数据库 / For connecting to MySQL database
from db import get_db_connection  # 自定义模块，用于获取数据库连接 / Custom module for getting database connection
from config import Config  # 自定义模块，用于加载配置 / Custom module for loading configuration
import random  # 用于生成随机数 / For generating random numbers
from openai import OpenAI  # OpenAI API 客户端 / OpenAI API client

# 初始化 Flask 应用 / Initialize Flask application
app = Flask(__name__)
CORS(app)  # 允许跨域请求 / Enable cross-origin requests

# 从配置中加载 OpenAI API 密钥 / Load OpenAI API key from configuration
OPENAI_API_KEY = Config.OPENAI_API_KEY

# 记录访问者信息 / Record visitor information
@app.route('/api/record-visit', methods=['POST'])
def record_visit():
    data = request.json  # 获取请求中的 JSON 数据 / Get JSON data from request
    fingerprint = data.get('fingerprint')  # 设备指纹 / Device fingerprint
    user_agent = data.get('user_agent')    # 用户浏览器信息 / User browser information
    ip_address = data.get('ip_address')    # IP 地址 / IP address

    if not fingerprint:
        return jsonify({'error': 'Fingerprint is required'}), 400  # 如果设备指纹缺失，返回错误 / If fingerprint is missing, return error

    conn = get_db_connection()  # 获取数据库连接 / Get database connection
    cursor = conn.cursor()  # 创建游标对象 / Create cursor object

    try:
        # 检查是否已经存在该设备指纹 / Check if the fingerprint already exists
        cursor.execute('SELECT id, count FROM visitors WHERE fingerprint = %s', (fingerprint,))
        visitor = cursor.fetchone()  # 获取查询结果 / Fetch the query result

        if visitor:
            # 如果已经存在，更新 count / If exists, update the count
            visitor_id = visitor[0]
            new_count = visitor[1] + 1
            cursor.execute('UPDATE visitors SET count = %s WHERE id = %s', (new_count, visitor_id))
        else:
            # 如果不存在，插入新记录 / If not exists, insert a new record
            cursor.execute(
                'INSERT INTO visitors (fingerprint, user_agent, ip_address, count) VALUES (%s, %s, %s, %s)',
                (fingerprint, user_agent, ip_address, 1)
            )
            visitor_id = cursor.lastrowid  # 获取插入记录的 ID / Get the ID of the inserted record

        conn.commit()  # 提交事务 / Commit the transaction
        return jsonify({'visitor_id': visitor_id}), 201  # 返回访问者 ID / Return visitor ID
    except Exception as e:
        conn.rollback()  # 回滚事务 / Rollback the transaction
        return jsonify({'error': str(e)}), 500  # 返回错误信息 / Return error message
    finally:
        cursor.close()  # 关闭游标 / Close the cursor
        conn.close()  # 关闭数据库连接 / Close the database connection

# 记录用户回答 / Record user response
@app.route('/api/record-response', methods=['POST'])
def record_response():
    data = request.json  # 获取请求中的 JSON 数据 / Get JSON data from request
    fingerprint = data.get('fingerprint')  # 设备指纹 / Device fingerprint
    question = data.get('question')        # 问题 / Question
    answer = data.get('answer')            # 回答 / Answer

    if not all([fingerprint, question, answer]):
        return jsonify({'error': 'Missing required fields'}), 400  # 如果缺少必要字段，返回错误 / If required fields are missing, return error

    conn = get_db_connection()  # 获取数据库连接 / Get database connection
    cursor = conn.cursor()  # 创建游标对象 / Create cursor object

    try:
        # 插入回答记录 / Insert response record
        cursor.execute(
            'INSERT INTO responses (visitor_id, question, answer) VALUES (%s, %s, %s)',
            (fingerprint, question, answer)
        )
        conn.commit()  # 提交事务 / Commit the transaction
        return jsonify({'message': 'Response recorded successfully'}), 201  # 返回成功信息 / Return success message
    except Exception as e:
        conn.rollback()  # 回滚事务 / Rollback the transaction
        return jsonify({'error': str(e)}), 500  # 返回错误信息 / Return error message
    finally:
        cursor.close()  # 关闭游标 / Close the cursor
        conn.close()  # 关闭数据库连接 / Close the database connection

# 使用 ChatGPT 生成问题 / Generate question using ChatGPT
def generate_question_with_chatgpt(fingerprint, content):
    try:
        # 从数据库中获取用户的最近一条回答 / Get the user's latest response from the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT question, answer FROM responses WHERE visitor_id = %s ORDER BY id DESC LIMIT 1',
            (fingerprint,)
        )
        last_response = cursor.fetchone()  # 获取查询结果 / Fetch the query result
        cursor.close()
        conn.close()

        # 构建 ChatGPT 的提示词 / Build the prompt for ChatGPT
        prompt = f"""
        Generate a multiple-choice question to help classify visitors based on their interests or industry.
        The website content is {content}
        Provide the question and three options, separated by newlines.
        Format the response as follows:
        Question: [Your question here]
        Option 1: [Option 1]
        Option 2: [Option 2]
        Option 3: [Option 3]
        """

        if random.random() < 0.7 and last_response:  # 70% 概率 / 70% probability
            last_question, last_answer = last_response
            prompt += f"\n\nAsk a different question based on the user's previous response:\nQuestion: {last_question}\nAnswer: {last_answer}"
        else:
            prompt += f"\nTry to find the visitor\'s background unrelated to engineering."

        # 调用 ChatGPT API / Call ChatGPT API
        openai_object = OpenAI(api_key=OPENAI_API_KEY)
        response = openai_object.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates multiple-choice questions."},
                {"role": "user", "content": prompt}
            ]
        )

        # 提取返回的内容 / Extract the returned content
        content = response.choices[0].message.content
        
        # 解析问题和选项 / Parse the question and options
        lines = content.split('\n')
        question = None
        options = []

        for line in lines:
            if line.startswith("Question:"):
                question = line.replace("Question:", "").strip()
            elif line.startswith("Option 1:") or line.startswith("Option 2:") or line.startswith("Option 3:"):
                option = line.split(":")[1].strip()
                options.append(option)

        if question and len(options) == 3:
            return {
                'question': question,
                'options': options + ['other'],  # 添加一个 "other" 选项 / Add an "other" option
            }
        else:
            raise ValueError("Failed to parse question and options from ChatGPT response.")
    except Exception as e:
        print(f"Error generating question with ChatGPT: {e}")
        return None

# 生成随机数学问题 / Generate random math question
def generate_random_math_question():
    num1 = random.randint(1, 20)  # 生成随机数 / Generate random number
    num2 = random.randint(1, 20)  # 生成随机数 / Generate random number
    operator = random.choice(['+', '-', '*', '/'])  # 随机选择运算符 / Randomly choose an operator
    
    # 计算正确答案 / Calculate the correct answer
    if operator == '+':
        correct_answer = num1 + num2
    elif operator == '-':
        correct_answer = num1 - num2
    elif operator == '*':
        correct_answer = num1 * num2
    elif operator == '/':
        correct_answer = num1 // num2  # 整数除法 / Integer division

    question = f'{num1} {operator} {num2} = ?'  # 构建问题 / Build the question
    options = [str(correct_answer), str(random.randint(1, 40)), str(random.randint(1, 40))]
    random.shuffle(options)  # 打乱选项顺序 / Shuffle the options

    return {
        'question': question,
        'options': options + ['other'],  # 添加一个 "other" 选项 / Add an "other" option
    }

# 生成问题 / Generate questions
@app.route('/api/generate-questions', methods=['POST'])
def generate_questions():
    data = request.json  # 获取请求中的 JSON 数据 / Get JSON data from request
    print(data)  # 打印请求数据 / Print request data
    fingerprint = data.get('fingerprint')  # 从请求中获取设备指纹 / Get fingerprint from request
    content = data.get('content')  # 获取内容 / Get content
    chatgpt_result = generate_question_with_chatgpt(fingerprint, content)  # 使用 ChatGPT 生成问题 / Generate question using ChatGPT
    if not fingerprint:
        math_question = generate_random_math_question()  # 生成随机数学问题 / Generate random math question
        return jsonify(math_question), 200
    if chatgpt_result:
        # 如果 ChatGPT 返回了有效结果，直接使用 / If ChatGPT returns a valid result, use it directly
        return jsonify(chatgpt_result), 200
    else:
        # 如果 ChatGPT 失败，生成随机数学问题 / If ChatGPT fails, generate a random math question
        math_question = generate_random_math_question()
        return jsonify(math_question), 200

# 启动 Flask 应用 / Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)  # 以调试模式运行 / Run in debug modecvgvbf