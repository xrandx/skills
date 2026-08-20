---
name: switch-to-china-docker-mirrors
description: 查询、验证并替换 Docker 基础镜像、APT 与 Python pip/uv 为国内源。用于中国网络下 Docker 构建下载慢或失败。
---

# 国内 Docker 源

1. 读取 `FROM`，创建或更新同目录 `Dockerfile.cn`。
2. 查询完整镜像名和固定标签：

   ```bash
   curl -fsS --get 'https://docker.aityp.com/api/v1/image' \
     --data-urlencode "search=$IMAGE" \
     --data-urlencode "site=${SITE:-All}" \
     --data-urlencode 'platform=linux/arm64'
   ```

3. 仅采用 `source`、平台完全匹配的 `mirror`；不改标签或依赖。
4. 有 `apt-get` 时读 [references/apt.md](references/apt.md)；有 pip/uv 时读 [references/python.md](references/python.md)。
5. 验证：

   ```bash
   docker build --check --platform linux/arm64 -f <Dockerfile.cn> .
   ```

报告替换项、未匹配项和验证结果。
