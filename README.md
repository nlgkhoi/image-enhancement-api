# Instruction

## Install linraries

```
pip install requirements.txt
```

## Testing API

- First, running the ./main.py file.

```
python main.py
```

## About the api

- The API receive raw JSON data.
- You have to post raw JSON data, which contains the element 'urls' having an array of images need to be enhanced. Here
  is an example.
  
- Method: `POST`
- Endpoint: `/enhance`
- Request body:
```json
{
	"urls": [
		"https://genk.mediacdn.vn/k:thumb_w/640/2014/mg-1235-3-1416328703227/cuu-sang-anh-bang-vai-thao-tac-don-gian-trong-photoshop.jpg",
		"https://cdn.chotot.com/VgLdQ9uGutyeCuuNZUoqj8OuRtkNHCW38C9mG79wm6Q/preset:view/plain/989aca426d1a4759a2be4ddfe824fcde-2712313909326265231.jpg"
	]
}
```
- Response:

```json
{
  "https://genk.mediacdn.vn/k:thumb_w/640/2014/mg-1235-3-1416328703227/cuu-sang-anh-bang-vai-thao-tac-don-gian-trong-photoshop.jpg": {
    "enhanced_url": "static/output/c87d44e6-0faf-11ec-98c4-acde48001122.jpg",
    "enhanced_score": 0.0385232438655613
  },
  "https://cdn.chotot.com/VgLdQ9uGutyeCuuNZUoqj8OuRtkNHCW38C9mG79wm6Q/preset:view/plain/989aca426d1a4759a2be4ddfe824fcde-2712313909326265231.jpg": {
    "enhanced_url": "static/output/c88e69f6-0faf-11ec-98c4-acde48001122.jpg",
    "enhanced_score": 0.005570224491517227
  }
}
```

