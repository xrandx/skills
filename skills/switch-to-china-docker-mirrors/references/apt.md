# APT

先读 `/etc/os-release`、架构和现有源。只换 URI，保留版本代号、组件和签名。

| 系统 | 源文件 |
|---|---|
| Debian 12 容器、13+ | `/etc/apt/sources.list.d/debian.sources` |
| Ubuntu 24.04+ | `/etc/apt/sources.list.d/ubuntu.sources` |
| 其他版本 | `/etc/apt/sources.list` |

镜像主机：`mirrors.aliyun.com`、`mirrors.tuna.tsinghua.edu.cn`、`mirrors.ustc.edu.cn`。

| 仓库 | 路径 |
|---|---|
| Debian | `/debian`、`/debian-security` |
| Ubuntu x86 | `/ubuntu` |
| Ubuntu ARM 等 | `/ubuntu-ports` |

按实际文件设置 `APT_SOURCES`：

```dockerfile
ARG APT_MIRROR=mirrors.aliyun.com
ARG APT_SOURCES=/etc/apt/sources.list.d/debian.sources
RUN sed -i \
      -e "s|deb.debian.org|${APT_MIRROR}|g" \
      -e "s|security.debian.org/debian-security|${APT_MIRROR}/debian-security|g" \
      -e "s|archive.ubuntu.com|${APT_MIRROR}|g" \
      -e "s|security.ubuntu.com|${APT_MIRROR}|g" \
      -e "s|ports.ubuntu.com|${APT_MIRROR}|g" \
      "${APT_SOURCES}" \
    && apt-get update
```

EOL 版本改用镜像站的 archive/old-releases 仓库。安全源可能有同步延迟；按安全要求决定是否替换。
