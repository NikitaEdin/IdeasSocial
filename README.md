# Twitter Clone 'Ideas' - Flask Web Development Project

## Project Overview
This is a university project developed as a part of a web development course; SET09103 2024-5 at Edinburgh Napier University.<br>
The aim of the project is to build a simplified clone of Twitter, using **Flask** as the backend framework.<br> 
The project demonstrates basic user interactions such as user creation, posting, following, and interacting with posts, showcasing the fundamental features of a social media platform.

## Features
- User Registration and Login functionality.
- Post Creation and Timeline features.
- User Following to enable following other users and seeing their posts _(planned)_.
- Likes and Comments on posts _(planned)_.
- Responsive Design for Seamless experience on both desktop and mobile devices.

## Tech Stack
- Backend: Flask (Python).
- Frontend: HTML, CSS, JavaScript, and Bootstrap5.
- Database: SQLAlchemy.
- Deployment: Deployed locally and on given university VMs.

<hr>

### Prerequisites
- [Python 3.x](https://www.python.org/downloads/)

### Installation Steps
Clone the repo and open in your editor of choice, preferably Visual Studio Code.

Execute the following commands in the Terminal:
- `python -m venv venv` to create a virtual environment.
- `venv\Scripts\activate` to activate the venv.

> [!NOTE]  
> If scripts are disabled on your system, execute:<br>
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Unrestricted`

- `pip install -r requirements.txt` to install all dependencies.
- Create a new file called `.env` in the root folder, and add the following:

```
SECRET_KEY=you_secret_key
DATABASE_URL=sqlite:///site.db
Debug=True
```

> [!TIP]  
> Replace `your_secret_key` with your actual key.

- `python run.py` - To launch the project.