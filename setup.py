
from setuptools import setup, find_packages

setup(
    name='pystom',          # 包名，换成你的库名
    version='0.1.0',                   # 版本号
    author='MoGui-Hao',
    author_email='mogui_hao@outlook.com',
    description='快速创建一个Minecraft服务器',
    long_description=open('README.md', encoding='utf-8').read(),  # 详细描述，通常从README.md读入
    long_description_content_type='text/markdown',               # README格式
    url='https://github.com/Mogui-Hao/PyStom',               # 项目主页
    packages=find_packages(),          # 自动查找包
    classifiers=[                     # 项目分类，方便PyPI展示
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # 许可证，根据实际情况修改
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',          # 支持的Python版本
    install_requires=[                # 依赖包列表
        # 'requests>=2.20.0',
        # 'numpy>=1.18.0',
    ],
)

