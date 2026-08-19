---
name: switch-to-china-docker-mirrors
description: 查询并验证国内 Docker 镜像，为镜像创建或更新 Dockerfile.cn。适用于中国网络环境下基础镜像拉取缓慢、失败或需要替换镜像源的场景。
---

# Docker 镜像替换

## 工作流程

1. 读取目标 Dockerfile 中的所有 `FROM` 镜像，并在同目录创建或更新 `Dockerfile.cn`；遵循仓库已有的目录约定。
2. 使用完整镜像名称和标签查询镜像，以 ARM64 为例，视情况采用其他平台：

   ```bash
   curl -fsS --get 'https://docker.aityp.com/api/v1/image' \
     --data-urlencode "search=$IMAGE" \
     --data-urlencode "site=${SITE:-All}" \
     --data-urlencode 'platform=linux/arm64'
   ```

示例:
https://docker.aityp.com/api/v1/image?search=gcr.io/google-containers/coredns:1.2

https://docker.aityp.com/api/v1/image?search=python&site=docker.io&platform=linux/arm64

https://docker.aityp.com/api/v1/image?search=python&site=All&platform=linux/arm64


3. 优先采用 `source` 完全匹配、`platform` 为 `linux/arm64` 且标签固定的 `mirror`。无精确结果时，报告原因；未经明确说明，不更换标签或应用依赖。
4. 仅替换镜像引用，保留其他构建内容。完成后执行：

   ```bash
   docker build --check --platform linux/arm64 -f <Dockerfile.cn> .
   ```

   必要时执行真实构建，并使用 `docker image inspect` 确认架构。

## 输出要求

验证所有镜像替换、标签变化、未匹配项和验证结果，并展示给用户验证
