---
name: call-graph
description: "当用户想要使用纯文本绘制调用图（Call Graph / Call Stack）时使用。"
---

# Call Graph

使用纯文本绘制调用调用图 (Call Graph / Call Stack)

要求：
1. 使用 Markdown 的 `text` 代码块，不生成图片文件。
2. 按“入口 → 下游调用”的顺序，从上到下展开。
3. 使用树形符号和缩进表示调用层级，例如：
   - `├──` 表示后续还有同级调用
   - `└──` 表示当前层级的最后一个调用
   - `│` 表示调用链仍在继续
4. 每个节点尽量包含：
   - 函数、方法、接口、组件或服务名称
   - 所属文件或模块
   - 一句简短注释，说明其职责
5. 对不同类型的调用进行标记：
   - 同步调用是默认类型，不添加 `[sync]` 或其他同步标记
   - 异步调用在节点注释的末尾添加 `，async`，例如 `[加密用户密码，async]`
   - `[callback]`：回调或事件触发
   - `[external]`：数据库、消息队列、HTTP API 等外部依赖
   - `[conditional]`：仅在特定条件下调用
6. 遇到分支、循环、递归或重复调用时：
   - 分别展示不同分支
   - 递归调用标记为 `[recursive]`
   - 已经展开过的节点使用 `↳ see above`，避免重复展开
7. 忽略无关的基础语法、简单 getter/setter 和没有业务意义的工具调用。
8. 默认最多展开 8 层；超过深度时标记为 `... omitted`。
9. 无法从代码中确认的调用关系标记为 `[uncertain]`，不要将其当作确定事实。
10. 在调用图之后，简要列出：
    - 入口节点
    - 核心业务链路
    - 外部依赖
    - 无法解析的动态调用

输出格式示例：

```text
apps/api/UserController.registerUser()              [HTTP 注册入口]
├── UserService.createUser()                        [services/UserService.ts，创建用户]
│   ├── UserValidator.validateRegistration()        [校验注册参数]
│   ├── PasswordService.hashPassword()              [加密用户密码，async]
│   └── UserRepository.insert()                     [写入用户数据，async]
│       └── Database.users.insert()                  [external，执行数据库写入]
├── EmailService.sendWelcomeEmail()                 [发送欢迎邮件，async]
│   └── MailProvider.send()                          [external，调用邮件服务]
└── AuditService.recordRegistration()               [callback，记录审计日志]
```