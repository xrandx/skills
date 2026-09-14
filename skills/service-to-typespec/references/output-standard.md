# 产物规范

以下为本 skill 的默认约定，不是 TypeSpec 官方强制目录标准。`output_dir` 存放 TypeSpec 源码与共享工具链，导出目录默认与其同级；沿用项目已有工具链与兼容的组织方式。

## 目录与构建

```text
<output_dir>/
├── package.json                 # 若已有 workspace 工具链则直接复用
├── <现有包管理器的锁文件>
├── scripts/                     # 共享构建与校验
├── README.md                    # 多服务时提供汇总阅读入口
└── <服务名>/
    ├── main.tsp                 # HTTP 入口，仅在适用时创建
    ├── asyncapi.tsp             # 消息入口，仅在适用时创建
    ├── tspconfig.yaml
    ├── tspconfig.asyncapi.yaml
    ├── <领域名>.tsp
    └── README.md
<output_dir 的父目录>/
├── openapi/
│   ├── .gitignore               # *.yaml、*.yml
│   ├── README.md                # 构建与预览命令
│   ├── index.html               # 预览入口（如项目使用）
│   └── <服务名>.openapi.yaml    # 可再生产物
└── asyncapi/
    ├── .gitignore
    ├── README.md
    ├── index.html
    └── <服务名>.asyncapi.yaml
```

例如 `output_dir=contracts/typespec` 时，导出到 `contracts/openapi` 和 `contracts/asyncapi`。用户显式指定的产物路径优先。

只创建实际需要的入口、配置和领域文件。纯消息服务可以只有消息入口。服务名默认沿用源码目录名；有重名或与 openapi、asyncapi、scripts 等保留目录冲突时采用稳定且唯一的名称，在 README 说明映射。

共享脚本支持全量和按服务构建，自动发现契约入口并排除工具与输出目录。输出集中存放，仅在协议适用时生成 YAML，不附加 JSON。YAML 是可再生 artifact，忽略规则放在各产物目录，不扩大根 `.gitignore` 的忽略范围；TypeSpec 配置 YAML 仍需版本管理。依赖由输出根目录或项目 workspace 管理，不为各服务建立 npm 项目。README 使用当前项目实际可执行的命令，不硬编码包管理器或绝对本机路径。

更新后不再适用的旧导出需核实来源；只清理属于本任务且可再生的文件，无法确认时说明其已失效，不能把它当成当前输出。没有该类接口与尚未查清必须区分。

## 命名与协议

- 文件用 kebab-case；namespace、model、enum、union、interface 用 PascalCase；operation 等遵循当前 TypeSpec 命名规范。
- 真实字段、路由、枚举值、事件名和已有 operationId 优先于命名风格。类型准确区分必填、可省略、null、默认值及约束。
- 每个服务使用清晰的 namespace，按业务领域拆分，入口显式 import；领域过大时再拆 models/operations，不要求每个类型单独一个文件。
- HTTP 与消息编译入口分离，避免消息操作被误导出为 HTTP 路由；相同语义的 payload 复用类型定义。
- AsyncAPI send/receive 以当前服务为主体。SSE 的 HTTP 连接归 OpenAPI，服务器消息归 AsyncAPI，payload 是解码后的 data；SSE 专属行为用有说明的扩展，不伪造标准 binding。

使用官方 formatter。每个 operation 的中文 `@summary` 和 `@doc` 必须分别表达功能摘要和详细行为，不能只翻译函数名、复制同一句话或用注释替代。OpenAPI 检查 summary/description；AsyncAPI 按所用 emitter 检查 title/summary 与 description，确保两类文本均保留。类型无法表达的业务约束写入 `@doc`。

## 简短 README

每个服务保留一份阅读入口，包含：

1. 服务职责、范围、源码位置及检查基线（提交、本地变更和相关配置条件）。
2. 领域与契约文件链接、关键源码入口及符号，帮助人和 agent 继续定位。
3. 影响使用者的关键行为与类型不能表达的约束，避免重复完整 schema。
4. 适用的协议、导出路径、实际构建/校验命令和结果，以及已发现/已建模接口、通道、消息数量。
5. 排除项、不适用协议的依据、未查清事项及所需证据。

多服务时根 README 仅汇总服务链接、适用导出及完成情况。不创建独立 YAML 索引或完整调用链文档；已有额外文件不自动删除。README 不记录凭据或真实用户数据，缺口与未执行检查如实说明。

## 预览说明

保留已有 README、预览页面及有效的预览命令，只调整与本次路径或工具链相关的内容。默认说明从仓库根目录进入对应产物目录，再运行 `npx --yes serve .`；打开终端实际输出的 Local 地址，不假设固定端口，不添加 Python 启动方式。保留项目已有的 Scalar 等替代命令，说明先构建 YAML、修改后重建刷新，以及页面使用 CDN 时的网络要求。

迁移输出时同步页面服务列表及 YAML 相对链接，并实际用浏览器验证渲染和服务切换；HTTP 200 不能代替显示验证。静态预览不调用真实业务接口或订阅事件流。

## 工具参考

用法以项目已安装版本为准，必要时查阅 [TypeSpec 命名规范](https://typespec.io/docs/handbook/style-guide/)、[配置](https://typespec.io/docs/handbook/configuration/configuration/) 和 [OpenAPI emitter](https://typespec.io/docs/emitters/openapi3/openapi/)。AsyncAPI emitter 查当前依赖的源码和说明，社区实现不等于 TypeSpec 官方实现。
