import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import os

class OpenPortsAnalysis:
    def __init__(self, ip_file):
        self.ip_file = ip_file
        self.data = self.load_ips()
        self.df = pd.DataFrame(self.data)
        self.log_file = 'analysis.log'
        self.csv_file = 'open_ports_data.csv'
        self.plot_file = 'open_ports_plot.png'
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logging.info('Logging setup complete.')

    def load_ips(self):
        try:
            with open(self.ip_file, 'r') as file:
                ips = file.readlines()
            # 处理IP数据，假定每行的格式为"IP地址,开放端口数量"。
            data = [line.strip().split(',') for line in ips if line.strip()]
            # 转换为字典格式
            return {'IP': [item[0] for item in data], 'Open Ports': [int(item[1]) for item in data]}
        except Exception as e:
            logging.error(f'Error loading IPs from file {self.ip_file}: {e}')
            raise

    def generate_csv(self):
        try:
            self.df.to_csv(self.csv_file, index=False)
            logging.info(f'CSV file generated: {self.csv_file}')
        except Exception as e:
            logging.error(f'Error generating CSV: {e}')
            raise

    def create_plot(self):
        try:
            sns.barplot(x='IP', y='Open Ports', data=self.df)
            plt.title('Open Ports per IP')
            plt.ylabel('Number of Open Ports')
            plt.xlabel('IP Address')
            plt.savefig(self.plot_file)
            plt.close()  # 关闭图表以释放内存
            logging.info(f'Plot saved as PNG: {self.plot_file}')
        except Exception as e:
            logging.error(f'Error creating plot: {e}')
            raise

    def run_analysis(self):
        self.generate_csv()
        self.create_plot()


if __name__ == '__main__':
    ip_file = 'ips.txt'  # 指定IP地址文件路径

    try:
        analysis = OpenPortsAnalysis(ip_file)
        analysis.run_analysis()
        print('Analysis completed successfully.')
    except Exception as e:
        print(f'An error occurred: {e}')
