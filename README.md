# Collaborative-Study
Welcome to CollabLearn, a web application designed to facilitate collaborative learning among students. This platform enables users to create or join study groups, communicate in real-time, and share resources like notes and files. Our goal is to help students stay organized, collaborate effectively, and make learning more engaging.

Note: This project is currently in its Minimum Viable Product (MVP) stage. An MVP is a version of a product with just enough features to be usable by early customers who can then provide feedback for future development. 


Features
User Registration and Authentication: Secure sign-up and login processes to protect user data.
Study Group Management: Create, join, and manage study groups tailored to specific subjects or projects.
Real-Time Messaging: Engage in instant communication within study groups to facilitate seamless collaboration.
Resource Sharing: Upload and manage group resources, including notes, files, and links.
User Profiles: Customize personal profiles with settings and preferences.
Activity Analytics: Monitor group activities to stay informed about participation and progress.
Tech Stack
Frontend: HTML, CSS, Basic JavaScript
Backend: Python, Flask, SQLAlchemy (ORM)
Database: MySQL
Installation
To set up the project locally:

Clone the Repository:

bash
Copy
Edit
git clone https://github.com/Henokgeta12/CollabLearn.git
cd CollabLearn
Set Up a Virtual Environment:

bash
Copy
Edit
python3 -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
Install Dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Configure the Database:

Ensure MySQL is installed and running.
Create a database named collablearn.
Update the database configuration in config.py with your MySQL credentials.
Apply Migrations:

bash
Copy
Edit
flask db upgrade
Run the Application:

bash
Copy
Edit
flask run
Access the application at http://127.0.0.1:5000/.

Usage
Register an Account: Sign up with your email and password.
Create or Join a Study Group: Search for existing groups or start a new one.
Collaborate: Use the messaging feature to communicate and share resources with group members.
Contributing
We welcome contributions to enhance CollabLearn. To contribute:

Fork the repository.
Create a new branch: git checkout -b feature/YourFeature.
Commit your changes: git commit -m 'Add YourFeature'.
Push to the branch: git push origin feature/YourFeature.
Open a pull request.
Please ensure your code adheres to our coding standards and includes relevant tests.

License
This project is licensed under the MIT License. See the LICENSE file for details.

Contact
For questions or feedback, please contact Henokgeta60@gmail.com.
