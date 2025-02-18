import React, { useState, useEffect } from 'react';
import './App.css';
import { useFingerprint, fetchIP } from './useFingerprint'; 

function App() {
    const [questions, setQuestions] = useState([
        {
          question: '1 + 1 = ?',
          options: ['0', '1', '2'],
        },
      ]); // 初始问题 / Initial questions
      const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0); // 当前问题的索引 / Current question index
      const [visitorId, setVisitorId] = useState(null); // 访问者 ID / Visitor ID
      const fingerprint = useFingerprint(); // 获取设备指纹 / Get device fingerprint
      const userAgent = navigator.userAgent; // 获取用户浏览器信息 / Get user browser information
      const [ipAddress, setIpAddress] = useState(null); // 存储 IP 地址 / Store IP address
      
      // 抓取网页内容并提取文本 / Fetch website content and extract text
    const fetchWebsiteContent = async (url) => {
        try {
        const response = await fetch(url);
        const html = await response.text();
    
        // 使用 DOMParser 提取文本内容 / Use DOMParser to extract text content
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
    
        // 提取 body 中的文本内容 / Extract text content from body
        const bodyText = doc.body.textContent || '';
    
        // 去除多余的空格和换行符 / Remove extra spaces and line breaks
        return bodyText.replace(/\s+/g, ' ').trim();
        } catch (error) {
        console.error('Error fetching website content:', error);
        return null;
        }
    };


      // 获取 IP 地址 / Get IP address
      useEffect(() => {
        const getIP = async () => {
          const ip = await fetchIP();
          setIpAddress(ip);
        };
    
        getIP();
      }, []);
    
      // 记录访问者信息（在设备指纹和 IP 地址生成后执行） / Record visitor information (executed after device fingerprint and IP address are generated)
      useEffect(() => {
        if (!fingerprint || !ipAddress) return; // 如果设备指纹或 IP 地址未生成，直接返回 / If device fingerprint or IP address is not generated, return directly
    
        const recordVisit = async () => {
          try {
            const visitResponse = await fetch('http://localhost:5000/api/record-visit', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                fingerprint: fingerprint,
                user_agent: userAgent,
                ip_address: ipAddress, // 使用获取到的 IP 地址 / Use the obtained IP address
              }),
            });
            const visitData = await visitResponse.json();
            setVisitorId(visitData.visitor_id); // 保存访问者 ID / Save visitor ID
          } catch (error) {
            console.error('Error recording visit:', error);
          }
        };
    
        recordVisit();
      }, [fingerprint, userAgent, ipAddress]);
    
      // 处理用户回答 / Handle user answer
      const handleAnswer = async (answer) => {
        if (!fingerprint || !visitorId) return; // 如果没有设备指纹或访问者 ID，直接返回 / If there is no device fingerprint or visitor ID, return directly
      
        try {
          // 抓取网页内容 / Fetch website content
          const websiteContent = await fetchWebsiteContent('https://samplelocalhost.com'); // 替换为你要抓取的 URL / Replace with the URL you want to fetch
      
          // 记录用户回答 / Record user answer
          const answerResponse = await fetch('http://localhost:5000/api/record-response', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              fingerprint: fingerprint,
              question: questions[currentQuestionIndex].question,
              answer: answer,
            }),
          });
          console.log('Answer recorded:', await answerResponse.json());
      
          // 生成新的问题 / Generate new questions
          const questionsResponse = await fetch('http://localhost:5000/api/generate-questions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              content: websiteContent || 'A Engineering student\'s portfolio website', // 使用抓取的内容或默认值 / Use fetched content or default value
              fingerprint: fingerprint,
              user_agent: userAgent,
              ip_address: ipAddress,
            }),
          });
          const newQuestion = await questionsResponse.json();
      
          // 更新问题列表 / Update questions list
          setQuestions((prevQuestions) => [...prevQuestions, newQuestion]);
          setCurrentQuestionIndex((prevIndex) => prevIndex + 1); // 切换到下一个问题 / Move to the next question
        } catch (error) {
          console.error('Error:', error);
        }
      };

  return (
    <div className="App">
      {/* 头部 / Header */}
      <header className="App-header">
        <h1>Welcome to My Personal Portfolio</h1>
        <p>
          Hi, I'm Zhiyuan(Mark) Li. Explore my work and get to know me better!
        </p>

        {/* 问题展示区域 / Questions display area */}
        <div className="questions-container">
          {questions.length > 0 && currentQuestionIndex < questions.length ? (
            <div className="question">
              <h3>{questions[currentQuestionIndex].question}</h3>
              <ul>
                {questions[currentQuestionIndex].options.map((option, i) => (
                  <li key={i} onClick={() => handleAnswer(option)}>
                    {option}
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            <p>No more questions!</p>
          )}
        </div>
      </header>

      {/* 个人简介 / About Me */}
      <section className="about-me">
        <div className="container">
          <h2>About Me</h2>
          <div className="about-content">
            <img src="images/photo_mark.jpg" alt="Profile" className="profile-image" />
            <div className="about-text">
              <p>
              I am a third-year Engineering Science (Robotics) student at the University of Toronto, deeply passionate about Machine Intelligence and Robotics. 
              With a strong foundation in mathematics, algorithm development, and system modeling, I enjoy tackling complex engineering challenges. 
              My experience spans mathematical modeling, application development, and user interface design, allowing me to bridge the gap between theoretical concepts and practical implementation. 
              </p>
              <p>
              Beyond coding, I have a deep love for music and creative expression. I enjoy playing the piano, composing original pieces, and engaging with rhythm-games. 
              I’m always eager to explore new ideas, feel free to reach out if you’d like to collaborate, exchange ideas, or just have a chat!
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 技能展示 / Skills */}
      <section className="skills">
        <div className="container">
          <h2>Skills</h2>
          <div className="skills-grid">
            <div className="skill">
              <h3>Software Development</h3>
              <ul>
                <li>Pytorch</li>
                <li>QtDesigner</li>
                <li>ROS</li>
                <li>Mujoco</li>
              </ul>
            </div>
            <div className="skill">
              <h3>Hardware Development</h3>
              <ul>
                <li>System Verilog</li>
                <li>C++ & Arduino IDE</li>
                <li>Circuit Analysis</li>
                <li>Solidworks</li>
              </ul>
            </div>
            <div className="skill">
              <h3>Mathematical modelling</h3>
              <ul>
                <li>Calculus & Real, Complex Analysis</li>
                <li>Statistics & Ordinary Combinatorics </li>
                <li>Ordinary & Partial Differential Equations </li>
                <li>Graph Theory</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* 项目经验 / Projects */}
      <section className="projects">
        <div className="container">
          <h2>Projects & Awards</h2>
          <div className="projects-grid">
            <div className="project">
              <h3>Delivery Turtle-bot</h3>
              <p>
              A delivery robot prototype capable of navigating a test environment and stopping at designated locations.
              </p>
              <a href="#" className="project-link">View Project</a>
            </div>
            <div className="project">
              <h3>Portfolio Website</h3>
              <p>
                A responsive portfolio website designed to showcase my skills and projects. Built with React, Flask and MySQL.
              </p>
              <a href="#" className="project-link">View Github</a>
            </div>
            <div className="project">
              <h3>Contest Awards</h3>
              <p>
                Top 154 in Putnam and member of UofT Winning Team. 2-time CMO participant. Honour roll in AMC & CEMC math contests.
              </p>
              <a href="#" className="project-link">View Awards</a>
            </div>
          </div>
        </div>
      </section>

      {/* 教育背景 / Education */}
      <section className="education">
        <div className="container">
          <h2>Education</h2>
          <div className="education-grid">
            <div className="education-item">
              <h3>Bachelor of Engineering Science & Robotics Specialization</h3>
              <p>University of Toronto, 2022 - 2027</p>
            </div>
            <div className="education-item">
              <h3>British Columbia Certificate of Graduation (Dogwood Diploma)</h3>
              <p>Pinetree Secondary School, 2019-2022</p>
            </div>
          </div>
        </div>
      </section>

      {/* 社交媒体链接 / Social Media Links */}
      <section className="social-media">
        <div className="container">
          <h2>Connect With Me</h2>
          <div className="social-links">
            <a href="https://github.com/markli1hoshipu" target="_blank" rel="noopener noreferrer">GitHub</a>
            <a href="https://www.linkedin.com/in/zhiyuan-li-36b894296/" target="_blank" rel="noopener noreferrer">LinkedIn</a>
            <a href="mailto:markzhiyuan.li@mail.utoronto.ca">Email</a>
          </div>
        </div>
      </section>

      {/* 页脚 / Footer */}
      <footer className="footer">
        <div className="container">
          <p>&copy; 2025 Zhiyuan Li. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

export default App;