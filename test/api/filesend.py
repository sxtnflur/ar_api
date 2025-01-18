import requests


# domain = "https://dinocarbone.ru/"
domain = "http://127.0.0.1:8000/"

def test_send_media():
    url = domain + "send_media"

    files = [
        ("photo", ("anyphoto.jpg", open("img.jpg", "rb"), "image/jpg")),
        ("video", ("anyvideo.mp4", open("qrobs.mp4", "rb"), "video/mp4"))
    ]

    res = requests.post(
        url=url, files=files
    )
    print(res)
    print(res.json())