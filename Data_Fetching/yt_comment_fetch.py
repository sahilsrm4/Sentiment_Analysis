def get_comments(video_id,google_api_key,requests):
    url = "https://www.googleapis.com/youtube/v3/commentThreads"
    params = {
        "part": "snippet",
        "videoId": video_id,
        "key": google_api_key,
        "maxResults": 100,
        "textFormat": "plainText"
    }

    comments = []
    print("Fetching Comments...")
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
    print("Comments Fetched")

    return comments

