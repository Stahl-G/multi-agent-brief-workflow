# MABW v0.3.0 — 摘要草稿

**状态**: Draft — 需要 red-team pass
**日期**: 2026-06-19

---

## 摘要

企业简报依赖一门让新人分析师花费数月才能掌握的手艺：写出不仅事实正确，还符合部门隐性品味与未明说的编辑偏好的简报。单 LLM 方案在这里双重失败——它无法保证事实正确性（没有审计轨迹，不可修复），也无法积累品味偏好（每次运行从零开始）。

2025-2026 年间，企业 AI 的前沿实践正在从对话式交互走向可交付、可审计、可治理的 agent 工作流。Anthropic 将 Claude Cowork 定位为"knowledge work agent"，可以读写本地文件、跨连接应用工作、执行多步骤任务，并生成带有来源引用的可交付成果 [A2]。其最佳实践文档将 recurring、multi-input、file-output 的知识工作定义为一种与 chat 截然不同的任务形态 [A3]。在金融领域，Kepler 将确定性基础设施作为信任与验证层，将 Claude 作为推理与解释层，每个数字追溯到具体 filing、page 和 line item [A5]。在数据分析领域，Anthropic 发现准确性主要是上下文与验证问题，而非代码生成问题——三类主要错误是概念歧义、数据过时和检索失败 [A4]。

MABW（多智能体简报工作流）在 recurring enterprise briefing 这个垂直场景里，把这条产业趋势具体化。正确性由四类合约范畴治理，通过文件状态控制面执行。品味被捕获在 audience_profile.md 和一个带 SHA-256 链式哈希的改进账本中——人类撰写、人类批准、冻结为每次运行的快照。证据由分阶段 claim pipeline 治理，最终收敛于 v0.8.3 Claim Freeze Transaction：agent 起草不含 ID 的 claim_drafts.json；Python 分配确定性 CL-#### ID 并冻结权威 claim_ledger.json。Orchestrator 委派专家角色；阶段完成事务与质量门禁在每个边界执行流程完整性。

v0.9 从 source-level traceability 推进到 evidence-span-level support sufficiency。目标不是证明真相或消除幻觉。目标是使质量随机性成为可观察、可归因、可阻断、可复现、可比较和可裁决的。v0.9 的最小路径是：Atomic Claim Graph → Evidence Span Registry → Claim-Support Matrix → Semantic Assessment as Proposal → Human Adjudication Queue → Coverage Gate → Release Eligibility Scorecard。语义模型可以评估、质疑、提出标签，但不能直接决定发布资格、声明支持真相或归档等级——这些由 schema、policy、adjudication state 和 blocking rules 推导。

在改进闭环层面，MABW 与 OpenAI Tax AI 的生产级模式独立收敛：自我改进不是 agent 自己反思自己，而是生产系统把失败变成可验证的工程任务 [A+1]。领导修改、审计发现、引用错配、支持不足，会被转成结构化 finding；只有可复现、可归类、可测试的问题，才进入改进队列，经过有边界的修复、同证据回归验证和人类审查后更新发布资格。

本报告记录了将企业简报转变为一个**可审计、可追溯、人类门禁的改进循环**——而非一个更聪明的提示词——的设计哲学、架构与实现基线。MABW 操作化语义支持充分性。MABW 不证明真相或消除幻觉。

---

## 与 v0.2.0 摘要的主要变更

| 维度 | v0.2.0 | v0.3.0 |
|------|--------|--------|
| 产业上下文 | 无 | 新增 Cowork、Kepler、data analytics、Tax AI 作为产业趋势证据 |
| v0.9 定位 | 仅提及改进账本 | 明确 transition: traceability → support sufficiency |
| 改进闭环 | 无 | 新增 Tax AI failure-to-finding-to-repair 模式 |
| 口径纪律 | 隐含 | 显式声明："MABW 操作化语义支持充分性。MABW 不证明真相或消除幻觉。" |
| 字数 | ~280 CJK 字 | ~680 CJK 字 |

---

## Red-team Checklist

- [ ] 无 "Anthropic proves MABW"
- [ ] 无 "MABW proves truth"
- [ ] 无 "MABW eliminates hallucination"
- [ ] 无 "Citations = support sufficiency"
- [ ] 无 "v0.9 已实现"（使用 "v0.9 的最小路径是"）
- [ ] 无 "MABW is self-improving"（使用 "MABW 与 Tax AI 的生产级模式独立收敛"）
- [ ] Anthropic 指标标注为 "reported industrial practice"
- [ ] Kepler 标注为 "official case study"
- [ ] Tax AI 标注为 "engineering case study"
- [ ] 口径声明在最后一段重复
