## Install on AWS EC2 Instance

- Clone the repo.
- Transfer the extracted files using FileZilla onto your EC2 instance.
- Extract into `/HelloWorld/` folder.
- Execute the following commnads in the terminal.

### Preparing Environment
- `CD` to project folder.
Execute the following to prepare venv:

```
python3 -m venv venv
source venv/bin/activate
pip install Flask
```

### Install Gunicorn
``` 
pip install gunicorn
gunicorn -b 0.0.0.0:8000 app:app
sudo nano /etc/systemd/system/helloworld.service
```

- Add the following into the new file, save and close.

```
[Unit]
Description=Gunicorn instance for flask app
After=network.target
[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/helloworld
ExecStart=/home/ubuntu/helloworld/venv/bin/gunicorn -b localhost:8000 app:app
Restart=always
[Install]
WantedBy=multi-user.target
```

### Reload Services
```
sudo systemctl daemon-reload
sudo systemctl start helloworld
sudo systemctl enable helloworld
```

### Install nginx
```
sudo apt-get install nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### Creating nginx config
```
sudo nano /etc/nginx/sites-available/default
```

- Add the following at the top of the file:
```
upstream flaskhelloworld {
	server 127.0.0.1:8000;
}
```

- Add the following in the middle, under proxy-pass section:
```
    proxy_pass http://flaskhelloworld;
```

- **IMPORTANT**: remove the defualt 404 line.


### Starting the server
`sudo systemctl restart nginx`
