## Install on Ubuntu virutal machine

- Clone the repo.
- Transfer the files using FileZilla onto the server.
- Execute the following commands in the ssh terminal _(`cd` to project folder)_:

### Preparing VM

```
sudo apt update
sudo apt install python3.10-venv
```

### Preparing VENV
```
python3 -m venv venv
source venv/bin/activate
```

### Installing requirements 
```
pip install -r requirements.txt
python3 create_env.py
python3 run.py
```