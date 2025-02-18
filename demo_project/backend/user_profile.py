import mysql.connector  # 用于连接 MySQL 数据库 / For connecting to MySQL database
from openai import OpenAI  # OpenAI API 客户端 / OpenAI API client
from config import Config  # 自定义模块，用于加载配置 / Custom module for loading configuration

# 从配置中加载 OpenAI API 密钥 / Load OpenAI API key from configuration
OPENAI_API_KEY = Config.OPENAI_API_KEY

# 连接到 MySQL 数据库 / Connect to MySQL database
def get_db_connection():
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,  # 数据库主机地址 / Database host address
        user=Config.MYSQL_USER,  # 数据库用户名 / Database username
        password=Config.MYSQL_PASSWORD,  # 数据库密码 / Database password
        database=Config.MYSQL_DB  # 数据库名称 / Database name
    )

# 获取第一个 visitor 及其所有回答 / Get the first visitor and all their responses
def get_visitor_and_responses():
    conn = get_db_connection()  # 获取数据库连接 / Get database connection
    cursor = conn.cursor(dictionary=True)  # 创建游标对象，返回字典格式的结果 / Create cursor object, return results as dictionaries

    try:
        # 获取第一个 visitor / Get the first visitor
        cursor.execute('SELECT * FROM visitors ORDER BY id ASC LIMIT 1')
        visitor = cursor.fetchone()  # 获取查询结果 / Fetch the query result

        if not visitor:
            print("No visitors found in the database.")  # 如果没有 visitor，打印提示信息 / If no visitors found, print message
            return None

        # 获取该 visitor 的所有回答 / Get all responses for this visitor
        cursor.execute('SELECT question, answer FROM responses WHERE visitor_id = %s', (visitor['fingerprint'],))
        responses = cursor.fetchall()  # 获取所有回答 / Fetch all responses

        return {
            'visitor': visitor,  # 返回 visitor 信息 / Return visitor information
            'responses': responses,  # 返回回答信息 / Return responses
        }
    except Exception as e:
        print(f"Error fetching data from database: {e}")  # 打印错误信息 / Print error message
        return None
    finally:
        cursor.close()  # 关闭游标 / Close the cursor
        conn.close()  # 关闭数据库连接 / Close the database connection

# 生成用户画像总结 / Generate user profile summary
def generate_user_profile_summary(visitor, responses):
    try:
        # 构建 ChatGPT 的提示词 / Build the prompt for ChatGPT
        prompt = f"""
        Based on the following visitor information and their responses, generate a summary of the user profile:
        
        Visitor Information:
        - Fingerprint: {visitor['fingerprint']}  # 设备指纹 / Device fingerprint
        - User Agent: {visitor['user_agent']}  # 用户浏览器信息 / User browser information
        - IP Address: {visitor['ip_address']}  # IP 地址 / IP address
        - Visit Count: {visitor['count']}  # 访问次数 / Visit count
        - First Visit: {visitor['created_at']}  # 首次访问时间 / First visit time

        Responses:
        {responses}  # 用户回答 / User responses

        Provide a concise summary of the user's interests, behavior, and potential industry or background.
        """

        # 调用 ChatGPT API / Call ChatGPT API
        openai_object = OpenAI(api_key=OPENAI_API_KEY)
        response = openai_object.chat.completions.create(
            model="gpt-3.5-turbo",  # 使用 GPT-3.5 模型 / Use GPT-3.5 model
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates user profile summaries."},
                {"role": "user", "content": prompt}
            ]
        )

        # 提取返回的内容 / Extract the returned content
        summary = response.choices[0].message.content
        return summary  # 返回生成的总结 / Return the generated summary
    except Exception as e:
        print(f"Error generating user profile summary: {e}")  # 打印错误信息 / Print error message
        return None

# 主函数 / Main function
def main():
    # 获取 visitor 及其回答 / Get visitor and their responses
    data = get_visitor_and_responses()
    if not data:
        return

    visitor = data['visitor']  # visitor 信息 / Visitor information
    responses = data['responses']  # 回答信息 / Responses

    # 打印 visitor 信息 / Print visitor information
    print("Visitor Information:")
    print(f"Fingerprint: {visitor['fingerprint']}")
    print(f"User Agent: {visitor['user_agent']}")
    print(f"IP Address: {visitor['ip_address']}")
    print(f"Visit Count: {visitor['count']}")
    print(f"First Visit: {visitor['created_at']}")
    # print("\nResponses:")
    # for response in responses:
    #     print(f"Question: {response['question']}")
    #     print(f"Answer: {response['answer']}")
    #     print("---")

    # 生成用户画像总结 / Generate user profile summary
    summary = generate_user_profile_summary(visitor, responses)
    if summary:
        print("\nUser Profile Summary:")
        print(summary)  # 打印用户画像总结 / Print user profile summary
    else:
        print("Failed to generate user profile summary.")  # 打印失败信息 / Print failure message

# 程序入口 / Program entry point
if __name__ == '__main__':
    main()  # 调用主函数 / Call main function