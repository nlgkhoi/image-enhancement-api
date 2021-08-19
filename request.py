import requests
import json

url = "http://127.0.0.1:5000/enhance"

payload = json.dumps({
  "urls": [
    "https://genk.mediacdn.vn/k:thumb_w/640/2014/mg-1235-3-1416328703227/cuu-sang-anh-bang-vai-thao-tac-don-gian-trong-photoshop.jpg",
    "https://th.bing.com/th/id/R.7924efd2efd3b67225ebb6cc82331bc8?rik=TKz8a7gW1Ur9zw&riu=http%3a%2f%2fpalistudio.com%2fupload%2fimage%2fdata%2fTin-tuc%2fChup-anh-cuoi%2fHa-Noi%2fZEN1242-d23a92.jpg&ehk=HgnL8rnD6HnJRBawFWnFTJC8HacfoC%2f75d5xrPwGDxI%3d&risl=&pid=ImgRaw&r=0",
    "https://genk.mediacdn.vn/k:thumb_w/640/2014/mg-1235-3-1416328703227/cuu-sang-anh-bang-vai-thao-tac-don-gian-trong-photoshop.jpg",
    "https://th.bing.com/th/id/R.7924efd2efd3b67225ebb6cc82331bc8?rik=TKz8a7gW1Ur9zw&riu=http%3a%2f%2fpalistudio.com%2fupload%2fimage%2fdata%2fTin-tuc%2fChup-anh-cuoi%2fHa-Noi%2fZEN1242-d23a92.jpg&ehk=HgnL8rnD6HnJRBawFWnFTJC8HacfoC%2f75d5xrPwGDxI%3d&risl=&pid=ImgRaw&r=0",
    "https://genk.mediacdn.vn/k:thumb_w/640/2014/mg-1235-3-1416328703227/cuu-sang-anh-bang-vai-thao-tac-don-gian-trong-photoshop.jpg",
    "https://th.bing.com/th/id/R.7924efd2efd3b67225ebb6cc82331bc8?rik=TKz8a7gW1Ur9zw&riu=http%3a%2f%2fpalistudio.com%2fupload%2fimage%2fdata%2fTin-tuc%2fChup-anh-cuoi%2fHa-Noi%2fZEN1242-d23a92.jpg&ehk=HgnL8rnD6HnJRBawFWnFTJC8HacfoC%2f75d5xrPwGDxI%3d&risl=&pid=ImgRaw&r=0",
    "https://genk.mediacdn.vn/k:thumb_w/640/2014/mg-1235-3-1416328703227/cuu-sang-anh-bang-vai-thao-tac-don-gian-trong-photoshop.jpg",
    "https://th.bing.com/th/id/R.7924efd2efd3b67225ebb6cc82331bc8?rik=TKz8a7gW1Ur9zw&riu=http%3a%2f%2fpalistudio.com%2fupload%2fimage%2fdata%2fTin-tuc%2fChup-anh-cuoi%2fHa-Noi%2fZEN1242-d23a92.jpg&ehk=HgnL8rnD6HnJRBawFWnFTJC8HacfoC%2f75d5xrPwGDxI%3d&risl=&pid=ImgRaw&r=0",
    "https://genk.mediacdn.vn/k:thumb_w/640/2014/mg-1235-3-1416328703227/cuu-sang-anh-bang-vai-thao-tac-don-gian-trong-photoshop.jpg",
    "https://th.bing.com/th/id/R.7924efd2efd3b67225ebb6cc82331bc8?rik=TKz8a7gW1Ur9zw&riu=http%3a%2f%2fpalistudio.com%2fupload%2fimage%2fdata%2fTin-tuc%2fChup-anh-cuoi%2fHa-Noi%2fZEN1242-d23a92.jpg&ehk=HgnL8rnD6HnJRBawFWnFTJC8HacfoC%2f75d5xrPwGDxI%3d&risl=&pid=ImgRaw&r=0"
  ]
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
