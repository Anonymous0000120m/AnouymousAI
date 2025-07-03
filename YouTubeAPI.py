import requests
import logging

# 配置日志
logging.basicConfig(
    filename='youtube_api.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class YouTubeAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://www.googleapis.com/youtube/v3/'

    def get_user_info(self, channel_id):
        url = f'{self.base_url}channels'
        params = {
            'part': 'snippet,contentDetails',
            'id': channel_id,
            'key': self.api_key
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # 抛出HTTPError异常
            user_info = response.json()
            logging.info('User info retrieved successfully.')
            return user_info
        except requests.exceptions.HTTPError as e:
            logging.error(f'Error retrieving user info: {e}')
            raise Exception(f'Error retrieving user info: {response.text}')

# 使用示例
if __name__ == '__main__':
    api_key = 'YOUR_API_KEY'  # 替换为你的API密钥
    channel_id = 'CHANNEL_ID'  # 替换为实际的YouTube频道ID
    
    youtube = YouTubeAPI(api_key)

    try:
        user_info = youtube.get_user_info(channel_id)
        print(user_info)
    except Exception as e:
        print(f'An error occurred: {e}')
