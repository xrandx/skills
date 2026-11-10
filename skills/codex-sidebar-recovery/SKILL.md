---
name: codex-sidebar-recovery
description: 排查并恢复 Codex 桌面应用丢失的本地 Project、侧边栏分区及聊天归属，尤其适用于切换账号后项目列表为空；也支持检查本地记忆是否保留、确认正在使用的记忆版本，以及切换 memories / memories_v2。提供备份和恢复流程；不用于找回云端项目或已删除聊天。
---

# Codex 本地项目与分区恢复

目标是恢复用户原有组织结构。先确认实际存储与界面状态；账号切换是一个已验证的原因，不能把所有空侧边栏都归因于它。

## 记忆检查与版本切换

用户询问记忆是否丢失、是否读取旧目录，或要求切回 `memories` 时，读取 [记忆检查与版本切换](references/memory-version.md)。该流程与侧边栏恢复独立：只恢复项目不构成修改记忆版本的授权。使用正式版本配置，不通过改目录名或覆盖数据库实现切换；版本切换不等于两套记忆内容已合并。

## 定位

1. 优先调用应用的 `list_projects`、`list_threads`，检查项目、分区、不可用主机和 grouping 设置。若记录存在，先解决折叠、视图或连接问题，不写磁盘配置。
2. 确定实际 Codex home；通常为 `~/.codex`，但不要覆盖环境中的 `CODEX_HOME`。运行：

   ```bash
   python3 scripts/recover.py inspect --state /absolute/codex-home/.codex-global-state.json
   ```

   脚本只输出各配置的项目名称、数量、分区摘要及 owner 标识；不读取登录凭据，不输出全部 atom 或聊天内容。
3. 如果当前 `local-projects` 为空，而 `electron-account-renderer-state-v1.inactive` 内存在用户要找回的完整项目，才走账号配置恢复。多个候选无法从项目名称判断时，向用户确认来源；不要默认取项目最多的账号。
4. 必要时以 SQLite `mode=ro` 检查 `state_5.sqlite` 的 `projects`、`project_roots`、`thread_sections`。先读 schema。数据库中有项目而应用 API 为空，是配置/加载问题的证据，不是删除数据的证据。不要直接改 SQLite、auth.json、账号 registry 或 owner。

## 准备恢复

```bash
python3 scripts/recover.py prepare --state /absolute/codex-home/.codex-global-state.json \
  --source SOURCE_OWNER --out /absolute/private-recovery-directory
```

使用新的恢复目录。检查输出项目名称、分区成员数、变化键；备份可能包含私人提示词，留在本机，不作为共享 skill 附件。

脚本仅迁移本地项目及相应组织字段，保留当前已有值；不会复制旧账号的云端项目、登录信息、权限、草稿或连接配置。分区按名称合并，优先保留当前分区 ID。若出现不支持的 schema、多份分区命名空间、相同 ID 的项目定义冲突，先停下检查，不用整份旧配置覆盖。

脚本针对已观察到的 legacy JSON schema。新版本可能将数据迁往其他位置；无匹配证据时不要强行造这些字段。

## 执行：必须在应用退出后写入

运行中的主进程可能覆盖外部修改；仅刷新窗口不够。先让用户知道应用即将退出，并检查是否有需要保留的运行任务。用户已授权恢复且可以重启时，不重复索要确认；有仍在工作的任务则先协调退出时机。

macOS 上确认真实应用路径和可执行文件，不能假定应用一定叫 Codex.app 或 ChatGPT.app。准备一个独立于当前工具会话的后台 worker（`subprocess.Popen(..., start_new_session=True)`，stdin 设为 DEVNULL，日志写入恢复目录），由同一个 worker 按顺序执行：

1. 留出短时间发送用户说明，然后通过 `osascript` 请求应用正常退出。不要 `kill -9`。
2. 轮询主进程是否退出，设定有限超时；检查退出状态，不把 `pgrep` 出错当作已退出。
3. 立即执行下列命令，并再次检查应用未启动：

   ```bash
   python3 scripts/recover.py apply --state /absolute/codex-home/.codex-global-state.json \
     --out /absolute/private-recovery-directory \
     --app-executable '/Applications/Actual.app/Contents/MacOS/Actual'
   ```

4. 只有 apply 成功后才 `open -a /Applications/Actual.app`。失败写日志并停止，不重复重启，不自动回滚整份配置。

不要让用户自己快速“退出再打开”，也不要在退出后额外 sleep 再写。已观察到的失败是：应用重新打开早于恢复写入，安全检查中止，导致看起来重启无效。若用户选择手动退出，明确让其等待 worker 自动打开。

上述自动重启流程仅在 macOS 验证；其他平台应采用平台对应的正常退出与启动方式。脚本的 apply 使用 macOS `pgrep`，不适配其他平台。

## 验证与恢复失败

- 读取恢复目录的 `status.json`，区分 prepared、restored 和异常；后台进程已启动不等于恢复成功。
- 重启后重新调用 `list_projects`、`list_threads`，核对原有项目、分区成员和代表性聊天归属，最后请用户确认界面。磁盘写入成功不能证明界面恢复。
- 如果 current owner、源配置或 UI schema 变化，重新 inspect 和 prepare；不要绕过保护。
- 若需撤销，在应用退出后比较 `before-apply.json` 与当前数据，只撤销本次修改的字段；不要丢掉恢复后产生的新记录。
- 最终说明恢复的数量、来源、验证结果和未完成事项。不要把本次个案写成产品承诺。

已验证案例：切换账号后当前项目列表为空，但旧账号快照内的 25 个项目、分区成员及本地数据库仍在；按以上顺序迁移配置后，用户确认恢复。这个数量不是脚本预设。
