import requests
import logging

# 配置日志
logging.basicConfig(
    filename='instagram_api.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class InstagramAPI:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = 'https://graph.instagram.com/'

    def get_user_info(self):
        url = f'{self.base_url}me'
        params = {
            'fields': 'id,username,account_type,media_count',
            'access_token': self.access_token
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
    access_token = 'YOUR_ACCESS_TOKEN'  # 替换为实际的用户访问令牌
    
    instagram = InstagramAPI(access_token)

    try:
        user_info = instagram.get_user_info()
        print(user_info)
    except Exception as e:
        print(f'An error occurred: {e}')
