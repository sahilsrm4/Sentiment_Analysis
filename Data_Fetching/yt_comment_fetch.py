import requests

google_api_key = 'AIzaSyAUTp9GIo46szx3Az_3Nh_HOF03AH4m9qM'
video_id = '8GY4m022tgo'

 
def get_comments(video_id):
    url = "https://www.googleapis.com/youtube/v3/commentThreads"
    params = {
        "part": "snippet",
        "videoId": video_id,
        "key": google_api_key,
        "maxResults": 100,
        "textFormat": "plainText"
    }

    comments = []
    while True:
        response = requests.get(url, params=params).json()
        for item in response.get("items", []):
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(comment)
        
        # Pagination handling
        if 'nextPageToken' in response:
            params['pageToken'] = response['nextPageToken']
        else:
            break

    return comments

# Example usage
comments = get_comments(video_id)
for comment in comments[:5]:
    print(comment)

with open('Fetched\comment.text','w',encoding='utf-8') as file:
    for comment in comments[:50]:
         file.write(comment+'\n')

 