# Twitter Clone 'Ideas' - Flask Web Development Project

## Project Overview
This is a university project developed as a part of a web development course; SET09103 2024-5 at Edinburgh Napier University.<br>
The aim of the project is to build a simplified clone of Twitter, using **Flask** as the backend framework.<br> 
The project demonstrates basic user interactions such as user creation, posting, following, and interacting with posts, showcasing the fundamental features of a social media platform.

## Features
- **Authentication & Authorisation**: Secure sign-up, login, and permission management.
- **Posting & Timeline**: Users can create posts and view a timeline of content.
- **Follow System**: Follow others to see their posts in user feed.
- **Likes & Comments**: Interact with posts via likes and comments.
- **Search & Hashtags**: Easily discover content with search and hashtag support.
- **User Profiles & Customisation**: Personalise profiles with settings and profile pictures.
- **Responsive Design**: Optimised for both desktop and mobile.
- **Admin Panel**: Tools for managing users and site activity.
- **API with Swagger**: API access with developer documentation (ready-only).

## Tech Stack
- Backend: Flask (Python).
- Frontend: HTML, CSS, JavaScript, and Bootstrap5.
- Database: SQLAlchemy.
- Deployment: Deployed locally and on given university VMs.

<hr>

### Prerequisites
- [Python 3.x](https://www.python.org/downloads/)

### Installation Steps
- Clone the repo and execute the following commands in the Terminal _(within project root folder)_:
- `python -m venv venv` to create a virtual environment.
- `venv\Scripts\activate` to activate the venv.

> [!NOTE]  
> If scripts are disabled on your system, execute:<br>
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Unrestricted`

- `pip install -r requirements.txt` to install all dependencies.
- `python run.py` - To launch the project.