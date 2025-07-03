import tweepy
import logging
import pandas as pd
import os

# 配置日志
logging.basicConfig(
    filename='twitter_api.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TwitterAPI:
    def __init__(self):
        # 从环境变量中获取API凭证
        self.api_key = os.getenv('API_KEY')
        self.api_key_secret = os.getenv('API_KEY_SECRET')
        self.access_token = os.getenv('ACCESS_TOKEN')
        self.access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')
        
        if not self.api_key or not self.api_key_secret or not self.access_token or not self.access_token_secret:
            raise ValueError("请确保所有API凭证都已设置在环境变量中。")

        self.api = self.authenticate()

    def authenticate(self):
        try:
            auth = tweepy.OAuthHandler(self.api_key, self.api_key_secret)
            auth.set_access_token(self.access_token, self.access_token_secret)
            api = tweepy.API(auth)
            # 检查认证是否成功
            api.verify_credentials()
            logging.info('Twitter API authentication successful.')
            return api
        except Exception as e:
            logging.error(f'Error during authentication: {e}')
            raise Exception('Authentication failed.')

    def get_user_info(self, username):
        try:
            user = self.api.get_user(screen_name=username)
            logging.info(f'User info retrieved for {username}')
            return {
                'username': user.screen_name,
                'name': user.name,
                'description': user.description,
                'followers_count': user.followers_count,
                'following_count': user.friends_count,
                'location': user.location
            }
        except tweepy.TweepError as e:
            logging.error(f'Error retrieving user info: {e}')
            raise Exception(f'Error retrieving user info: {str(e)}')

    def save_to_csv(self, user_info, directory='data', filename='user_info.csv'):
        # 确保目录存在
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        df = pd.DataFrame([user_info])
        file_path = os.path.join(directory, filename)
        df.to_csv(file_path, index=False, mode='a', header=not os.path.isfile(file_path))
        logging.info(f'User info saved to {file_path}.')

# 使用示例
if __name__ == '__main__':
    twitter = TwitterAPI()

    username = 'Twitter'  # 替换为实际的Twitter用户名
    try:
        user_info = twitter.get_user_info(username)
        print(user_info)
        twitter.save_to_csv(user_info)
    except Exception as e:
        print(f'An error occurred: {e}')
