# lazyMossAPI

> 一个简单的库,用于向MossFrp API发送请求

## 快速开始

#### 登录

```python
from lazyMossAPI.MossFrpAPI import MossFrpAPI
api = MossFrpAPI()
result = api.login("your_email@example.com","your_passwd")
if result:
    print("Succeed.")
```