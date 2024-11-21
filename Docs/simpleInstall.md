### Install on Windows via Visual Studio Code

- Clone the repo and execute the following commands in the Terminal _(within project root folder)_:
- `python -m venv venv` to create a virtual environment.
- `venv\Scripts\activate` to activate the venv.

> [!NOTE]  
> If scripts are disabled on your system, execute:<br>
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Unrestricted`

- `pip install -r requirements.txt` to install all dependencies.
- `python run.py` - To launch the project.