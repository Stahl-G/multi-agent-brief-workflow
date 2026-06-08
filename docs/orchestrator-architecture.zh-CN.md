# Orchestrator 架构

本页用公开安全方式说明 v0.6 Orchestrator 架构。

## 核心模型

Orchestrator 是 runtime main agent。它可以是 Hermes parent agent、Claude Code command context、Codex main agent、OpenCode primary agent，或 manual fallback 操作者。

Python 保持工具层定位，负责 workspace setup、source handling、deterministic checks、validation helpers、audit support 和 final rendering。Python 不是标准完整 brief-generation runtime。

```text
runtime main agent
  -> reads workspace context
  -> reads contract references
  -> identifies the next stage
  -> delegates a specialist role
  -> checks the expected artifact
  -> decides continue / retry / repair / review / block / finalize
```

## Contract References

v0.6.0 引入公开安全的 contract references：

- `configs/orchestrator_contract.yaml`
- `configs/stage_specs.yaml`
- `configs/artifact_contracts.yaml`
- `configs/policy_packs/default.yaml`

这些文件描述共享 authority、decision vocabulary、stage order、artifact expectations 和 default policy shell。它们不实现持久化 runtime state，也不执行 artifact registry validation。

## 四类 Contract

| 类别 | 目的 |
|---|---|
| Behavior | 定义 Orchestrator 和 specialist role 边界。 |
| Process / Artifact | 定义 stage readiness 和 expected artifact categories。 |
| Fact-Grounding / Evidence | 保持 material statements 可追溯到 supported claims。 |
| Quality / Audience | 让 delivery decisions 匹配 reader context。 |

## Decision Vocabulary

Orchestrator 使用统一 decision vocabulary：

- `continue`
- `retry_stage`
- `delegate_repair`
- `request_human_review`
- `block_run`
- `finalize`

在 v0.6.0 中，这些 decision 是 runtime entry 和 handoff artifacts 的 contract language。持久化 event log 和 runtime state 属于后续 milestone。

## Runtime Loop

每个 runtime 都应表达同一套 loop：

1. 读取 `config.yaml`、`sources.yaml`、`user.md`、inputs 和 handoff artifacts。
2. 从 handoff 读取 contract references。
3. 判断当前 stage 和 expected artifact。
4. 将 stage 委派给对应 specialist role 或 Python tool。
5. 检查 expected artifact 是否存在，并是否适合进入下一 stage。
6. 决定 continue、retry、delegate repair、request human review、block 或 finalize。
7. 仅在 audit readiness 后 finalize。

不同 runtime 的机制可以不同，但 artifact expectations 不应分叉。

## Provenance Compatibility

v0.6.0 不构建 provenance graph。但 contract 形状要兼容后续 provenance 工作，保留：

- artifact identity
- producer stage or role
- consumer stage or role
- validation result summary
- blocking reason
- retry or human-review decision
- decision category attached to a stage

## Deferred Work

后续 v0.6 milestone 负责：

- persisted runtime state
- minimum artifact registry
- feedback issue handling
- bounded repair
- material-fact and freshness gates
- public-safe evaluation cases
- evidence and execution provenance

## Related

- [Orchestrator Contract 模型](orchestrator-contracts.zh-CN.md)
- [当前架构状态](architecture-status.zh-CN.md)
- [迁移说明](MIGRATION.zh-CN.md)
- [v0.6.0 Explicit Orchestrator Contract](implementation/v0.6.0-explicit-orchestrator-contract.md)
