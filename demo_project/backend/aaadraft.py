from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from db import get_db_connection

from config import Config
from openai import OpenAI
# test db

# conn = get_db_connection()
# cursor = conn.cursor()
# cursor.execute('INSERT INTO visitors (fingerprint) VALUES (%s)', ('123edasdk',))
# visitor_id = cursor.lastrowid
# conn.commit()
# cursor.close()
# conn.close()


# conn = get_db_connection()
# cursor = conn.cursor()
# cursor.execute('DELETE FROM responses WHERE visitor_id = %s', ('123edasdk',))
# cursor.execute('DELETE FROM visitors WHERE fingerprint = %s', ('123edasdk',))
# conn.commit()
# cursor.close()
# conn.close()



def generate_question_with_chatgpt():
    try:
        # 设置 ChatGPT 的提示词
        prompt = """
        Generate a multiple-choice question related to technology, business, or general knowledge.
        Provide the question and three options, separated by newlines.
        Format the response as follows:
        Question: [Your question here]
        Option 1: [Option 1]
        Option 2: [Option 2]
        Option 3: [Option 3]
        """

        # 调用 ChatGPT API
        openai_object = OpenAI(api_key = '')
        response = openai_object.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates multiple-choice questions."},
                {"role": "user", "content": prompt}
            ]
        )

        # 提取返回的内容
        content = response.choices[0].message.content
        
        # 解析问题和选项
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
                'options': options,
            }
        else:
            raise ValueError("Failed to parse question and options from ChatGPT response.")
    except Exception as e:
        print(f"Error generating question with ChatGPT: {e}")
        return None

print(generate_question_with_chatgpt())