<div style="font-family: monospace;">

<div style="text-align:center;text-decoration:none;">

# [\</> Suspicious Link](http://4xk0.xyz/)

</div>

---

Suspicious Link is a lightweight web app written in [Flask](https://flask.palletsprojects.com/en/2.1.x/) which lets you create a somewhat suspicious link alias:

```
https://github.com/chr3st5an -> http://4xk0.xyz/04323142tcpipscreen-killer?deleteAll=true
```

![Suspicious Link photo](https://i.imgur.com/hRIzvPj.jpg)

You can visit the webpage of Suspicious Link [here](http://4xk0.xyz)

</br>

## Rick Roll

---

The web app is configured to redirect any HTTP GET request whose subpath is not part of the website nor part of a suspicious link alias to a rick roll:

> http://4xk0.xyz/ADDICT-21012902/VIDEO-hack390203/download.exe

</br>

## No Script

</br>

<div style="text-align:center;color:red;">

### ~~\<script>\</script>~~

</div>

</br>

The web page is made with HTML & CSS and doesn't use any JavaScript

</br>

## What Data Gets Stored

---

The web app uses MongoDB as database. It only stores generated aliases and their destination URL along with the creation date. That's it.

</br>

</div>

</br>

## API

---

### Create Suspicious Links

Endpoint: `POST /api/create-link`

```python
# Python
import requests


data = {
    "url": "https://youtube.com/"
}


r = requests.post("http://.../api/create-link", data=data)
```

```curl
curl -X POST -d "url=http://youtube.com" http://.../api/create-link
```

JSON-Response:

```json
{
    "alias": "http://.../",
    "error": null,
    "code" : 201
}
```

</br>

<div style="text-align:center">

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white)
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)

Made with <span style="color:red">&hearts;</span> by @chr3st5an

</div>
