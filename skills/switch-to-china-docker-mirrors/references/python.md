# Python

选一个地址：

- 阿里云：`https://mirrors.aliyun.com/pypi/simple/`
- 腾讯云：`https://mirrors.cloud.tencent.com/pypi/simple/`
- 火山引擎：`https://mirrors.volces.com/pypi/simple/`
- 华为云：`https://mirrors.huaweicloud.com/repository/pypi/simple/`
- 清华大学：`https://pypi.tuna.tsinghua.edu.cn/simple/`
- 中国科学技术大学：`https://pypi.mirrors.ustc.edu.cn/simple/`

## pip

```dockerfile
ENV PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
```

单次：`pip install --index-url <URL> <包>`。

## uv

在 `pyproject.toml` 添加：

```toml
[[tool.uv.index]]
name = "aliyun"
url = "https://mirrors.aliyun.com/pypi/simple/"
default = true
```
