from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    author="MojaveHao",
    author_email="HTTcode2020@126.com",
    name='lazyMossAPI',
    version='0.0.1',
    license="AGPLv3",
    packages=find_packages(),
    install_requires=[
        "requests"
    ],
    description="一个简单的用于请求MossFrp API的库",
    long_description_content_type='text/markdown',
    long_description=long_description,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent',
    ],
    python_requires=">3.6",
)