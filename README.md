Mini Challenge – Web Scraper for Visitor Classification

Description:
Build a tool that takes a website URL as input, scrapes its content, and classifies visitors based on their interests or industry. Your solution should dynamically generate questions and multiple-choice options to help categorize users visiting the site. We encourage you to be creative and go above and beyond the basic requirements.

For inspiration and a better understanding of our work, please feel free to visit chatsimple.ai.

Technical Requirements:

Frontend: React, Redux
Backend & Cloud: Python, Flask, AWS
Please provide the following:

GitHub Repository URL: Ensure your repository is publicly accessible. We’ll be looking for clean code, good practices, and thorough documentation.

Short Video Demo: A brief video (a few minutes) demonstrating your project and explaining your approach.


-------------------------------------------


Overall strategy:

Collect info -> Store info -> Analyze info


1. Setting up Database using MySQL
    Ensure Loading / Reading of Data 
    Enable delete table / create new table for new features

2. Write app/function/file to analyze user features, simply by sending them to AI
    Ensure connection to AI, send / read

3. Set up Basic webpage using React, a webpage with some content.
    Ensure localhost, visiting, style, content, ...

4. Set up a space for the question interactions
    Add a default question / something, ...

5. Use Flask to connect to frontend
    Random generate some questions for users, display with choices
    Record user input, load to database

6. Recheck Step 2, now with some user data.
