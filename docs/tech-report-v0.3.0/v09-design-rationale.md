# v0.9 Design Rationale: From Traceability to Support Sufficiency

**Purpose**: Connect Claude/Anthropic industrial evidence to MABW v0.9 control surfaces
**Created**: 2026-06-19
**Status**: Draft — requires red-team pass before insertion

---

## 概述

MABW v0.8.3 实现了 source-level traceability：每条声明可以追溯到其来源、进入工作流的步骤、冻结时间和门禁记录。但 traceability 不等于 support sufficiency——有来源不代表被支持，能追溯不代表被证明。

v0.9 的目标是建立 **evidence-span-level support sufficiency**：每条原子声明不仅有来源记录，还有证据跨度标注、支持度标签、修复责任人、裁决队列和发布资格评估。

以下将 v0.9 的五个新控制面与 Anthropic 产业实践证据建立连接。

---

## 1. Atomic Claim Graph（原子声明图）

### v0.9 定义

将复合声明分解为原子单元，每个原子声明有唯一 ID、角色（finding / interpretation / recommendation / context）、来源引用和可独立验证的支持记录。

### 产业连接

Anthropic 的数据分析实践 [A4] 发现，80% 的错误答案在检索到的语料中实际包含正确信息——问题不在于"没有来源"，而在于 agent 无法将正确的信息片段映射到正确的子问题。这正是 atomic claim 要解决的：不是"这条声明有没有来源"，而是"这条声明的每个子主张是否被对应的证据片段支持"。

Kepler [A5] 在金融领域将每个数字追溯到 filing/page/line item——这是 atomic claim 在数值领域的等价物。MABW 将同样的粒度应用到管理简报的文本声明。

### 引用措辞

> Business analytics accuracy failures often arise not from missing sources but from misalignment between information fragments and sub-questions [A4]. MABW's Atomic Claim Graph addresses this by decomposing compound claims into independently verifiable units, analogous to Kepler's line-item traceability in financial workflows [A5].

---

## 2. Evidence Span Registry / Evidence Capsule（证据跨度注册表）

### v0.9 定义

每条证据片段（evidence span）注册其来源、定位（section/page/paragraph）、提取时间、新鲜度标签和提取 agent ID。证据胶囊（evidence capsule）封装一个或多个 evidence spans 及其元数据。

### 产业连接

Anthropic 的 Citations API [B4] 实现了 passage-level citation：将用户文档分块为句子，模型引用具体句子。但这只是 traceability——passage-level citation 不等于 support sufficiency。

Kepler [A5] 的 end-to-end provenance 从 source document 到 filing/page/line item 建立完整链条。MABW 的 Evidence Span Registry 将同样的溯源链应用到 briefing 领域，但增加了 support label（支持 / 弱支持 / 矛盾 / 遗漏 / 不适用）——这是 Citations API 没有覆盖的维度。

### 引用措辞

> Passage-level citation [B4] provides traceability; it does not provide support sufficiency. MABW's Evidence Span Registry extends beyond citation to include support labels, freshness metadata, and extraction provenance—closer to Kepler's end-to-end provenance model [A5] than to sentence-level citation.

---

## 3. Claim-Support Matrix（声明-支持矩阵）

### v0.9 定义

将 Atomic Claim Graph 中的每条声明与 Evidence Span Registry 中的证据片段建立矩阵关系。每个 cell 标注支持度（supported / weakly_supported / contradicted / missing / not_applicable）和不确定性标记。

### 产业连接

Anthropic 的数据分析实践 [A4] 使用 semantic layer 作为"结构化真相源"——agent 被要求首先查询语义层，而非直接检索原始数据。这本质上是一个 claim-to-canonical-source 映射机制。

MABW 的 Claim-Support Matrix 是这一思路在 management briefing 领域的泛化：不是"agent 是否找到了数据"，而是"每条声明是否被足够的证据跨度以足够的强度支持"。

Kepler [A5] 的 stage-level eval 在 pipeline 每个阶段比较输出与已知正确答案。MABW 的 Claim-Support Matrix 不做"正确性判断"，而是做"支持充分性记录"——它不回答"这条声明对不对"，而是回答"这条声明被什么支持、支持到什么程度、有什么遗漏或矛盾"。

### 引用措辞

> Anthropic's analytics team uses semantic layers as structured sources of truth, requiring agents to query canonical definitions before raw data [A4]. MABW's Claim-Support Matrix generalizes this from analytics metrics to management-brief claims: each atomic claim is mapped to its evidence spans with explicit support labels, enabling support sufficiency assessment without claiming truth verification.

---

## 4. Semantic Assessment as Proposal, Not Authority（语义评估作为提案而非权威）

### v0.9 定义

语义评估 agent 可以提出 support labels、uncertainty markers 和 disagreement flags，但不能直接决定 release eligibility、claim support truth 或 archive/reference grade。最终裁决由 schema、policy、adjudication state 和 blocking rules 推导。

### 产业连接

Anthropic 在多智能体协调模式 [A10] 中明确警告：generator-verifier 模式只有在评估标准明确时才有效。"A verifier told only to check whether output is good, with no further criteria, will rubber-stamp"——这"creates the illusion of quality control without the substance" [A10]。

MABW v0.9 的设计直接回应了这一警告：semantic assessor 不是笼统的"好不好"检查器，而是按 explicit criteria（claim role、evidence span、support label schema）产出结构化提案。最终裁决权不在 assessor，而在 adjudication queue 和 release eligibility scorecard。

Kepler [A5] 同样将模型放在 pipeline 的一个阶段而非整个系统。模型负责推理和解释，确定性基础设施负责验证和溯源。MABW 将这一分离原则应用到语义评估：模型评估支持充分性，Python 冻结评估结果、执行门禁规则、计算发布资格。

### 引用措辞

> Multi-agent verification loops require explicit criteria; otherwise they create an illusion of quality control [A10]. MABW v0.9 operationalizes this by making semantic assessment a proposal layer: the assessor produces structured support records, uncertainty markers, and disagreement flags according to explicit schemas, but release eligibility is derived deterministically from policy, adjudication state, and blocking rules—never from the assessor's own judgment.

---

## 5. Human Adjudication Queue（人类裁决队列）

### v0.9 定义

当 Claim-Support Matrix 中出现 contradicted、missing 或 weakly_supported 标记，且无法由确定性规则自动解决时，该声明进入 adjudication queue 等待人类裁决。裁决结果记录在 claim ledger 中，具有完整的审计轨迹。

### 产业连接

Kepler [A5] 的架构中，人类分析师可以"with a single click"追溯每个数字到源文件中的精确行项——这是 human-in-the-loop 的设计前提：只有当系统提供了足够的结构化信息，人类才能做出有效裁决。

Anthropic 的 Zero Trust 框架 [A7] 将 human approval 作为 agent 治理的核心控制面之一。MABW 的 adjudication queue 是这一原则在 briefing 领域的实现：不是"人类审核整篇简报"，而是"人类只审核系统无法确定性解决的特定声明"。

### 引用措辞

> Kepler enables human analysts to trace any number to its source with a single click, providing the structured context needed for effective human judgment [A5]. MABW's adjudication queue applies the same principle: humans are not asked to review entire briefs, but to adjudicate specific claims that deterministic rules cannot resolve—supported by full claim-to-evidence traceability.

---

## 6. Coverage and Omission Gate（覆盖率与遗漏门禁）

### v0.9 定义

在 Claim-Support Matrix 完成后，检查是否有预期覆盖的主题维度未被任何声明覆盖（结构性遗漏），或有声明的 evidence span 全部标记为 missing（证据缺失）。

### 产业连接

Anthropic 的数据分析实践 [A4] 使用 ablation study 和 fixed offline eval set 来检测遗漏——如果移除某个组件后 pass rate 下降，说明该组件承担了关键功能。MABW 的覆盖率门禁将同样的逻辑应用到 briefing：如果某个预期维度在 matrix 中没有对应的 claim-evidence 对，说明存在结构性遗漏。

### 引用措辞

> Anthropic uses ablation studies to detect component-level coverage gaps in analytics pipelines [A4]. MABW's coverage gate applies the same principle to briefing completeness: if an expected topic dimension has no corresponding claim-evidence entries in the matrix, it signals a structural omission that must be addressed before release.

---

## 7. Release Eligibility Scorecard（发布资格评估卡）

### v0.9 定义

综合 Claim-Support Matrix 的支持度分布、adjudication queue 的未解决项、coverage gate 的遗漏标记、freshness metadata 的过时比例，计算一个结构化的发布资格评估。不通过的声明或维度被阻断、降级或标记为非参考状态。

### 产业连接

Anthropic 的数据分析团队要求 domain owners 在 agent 发布前达到约 90% 的准确率阈值 [A4]。这是一个 release eligibility gate——不是"agent 能不能回答"，而是"agent 的回答是否达到了可发布的质量标准"。

Kepler [A5] 的 stage-level eval 在每个 pipeline 阶段比较输出与已知正确答案。MABW 的 Release Eligibility Scorecard 将同样的阶段性评估应用到 briefing 的最终交付：不是"简报写完了"，而是"简报的每条声明都有足够的证据支持，未解决的裁决项已处理，覆盖率已验证"。

### 引用措辞

> Anthropic requires domain owners to clear ~90% accuracy thresholds before releasing analytics agents to stakeholders [A4]. Kepler runs stage-level evaluations comparing outputs against known-correct answers at every pipeline stage [A5]. MABW's Release Eligibility Scorecard combines both patterns: structured quality thresholds applied at delivery time, with support sufficiency metrics derived from the Claim-Support Matrix rather than raw accuracy.

---

## 8. Quality Pack System（质量包系统）

### v0.9 定义

将 audience_profile、improvement ledger、reference samples、quality gates 打包为可版本化、可分发、可撤销的 quality packs。每个 pack 有 SHA-256 哈希链、人类批准记录和快照机制。

### 产业连接

Anthropic 的 Agent Skills [B3] 将指令、脚本、资源打包进文件夹，让 agent 动态加载领域专业知识。Plugins [B7] 将 skills、hooks 和 MCP 配置打包为可安装包，支持私有 marketplace 分发。

但 Skills 和 Plugins 的安全风险也被明确指出：恶意 skill 可能引入漏洞或引导 agent 泄露数据 [B3]。MABW 的 Quality Pack System 通过 approval、hash chain、snapshot 和 revocation 机制来应对这一风险——每个 pack 必须经过人类批准，内容通过哈希链保护，运行时冻结为快照，可被撤销。

### 引用措辞

> Agent Skills bundle instructions, scripts, and resources for dynamic domain expertise loading [B3]; Plugins package skills, hooks, and MCP configurations for organizational distribution [B7]. Both introduce security risks requiring trust verification [B3]. MABW's Quality Pack System applies approval, hash-chain integrity, per-run snapshots, and revocation to the same packaging pattern—treating briefing domain knowledge as governed artifacts rather than free-form configuration.

---

## 9. Finding Candidate System（发现候选系统）

### v0.9+ 定义（建议）

当 Claim-Support Matrix、coverage gate、audit report 或 human feedback 中出现可复现的问题时，系统将其转为结构化的 Finding Candidate。每个 finding 有唯一 ID、受影响的 claim 和 evidence span、期望行为、回归测试用例、修复范围定义和人类决策记录。

### 产业连接

OpenAI Tax AI [A+1] 的改进闭环是目前最完整的生产级范例。其核心洞察是：**自我改进不是 agent 自己反思自己，而是生产系统把失败变成可验证的工程任务。**

Tax AI 的 `/candidates/FIND-RENTAL-0042/` 结构包含：repo、task.yaml、EXEC_PLAN.md、RESULTS.md、相关产品代码、eval datasets、eval suites、graders、skills、docs、只读 production trace 和 source artifacts [A+1]。Codex 不是拿模糊报错去修改代码，而是拿到一个有边界的任务环境。

关键约束：并非每个从业者修正都会自动变成 Codex 任务。修正可能代表提取遗漏、映射问题、产品不支持、税务判断，或者工作流噪声；只有反复差异经过审查并归并成可执行发现后，才会转成有边界、成功条件明确的任务 [A+1]。

MABW 与之独立收敛到同一类结构：

```text
findings/FIND-CLAIM-0042/
  finding.yaml              # 发现元数据
  affected_claims.json      # 受影响的声明
  affected_atoms.json       # 受影响的原子声明
  evidence_spans.json       # 相关证据跨度
  support_rows.json         # 支持度记录
  expected_behavior.md      # 期望行为描述
  regression_case.yaml      # 回归测试用例
  repair_scope.md           # 修复范围定义
  human_decision.md         # 人类决策记录
  results.md                # 修复结果
```

MABW 的"自我改进"闭环：

```text
report failure（报告失败）
→ claim-level trace（声明级追溯）
→ structured finding（结构化发现）
→ eval target（评测目标）
→ scoped repair（有边界修复）
→ same-evidence regression（同证据回归）
→ human review（人类审查）
→ release eligibility update（发布资格更新）
```

### 引用措辞

> OpenAI's Tax AI case demonstrates that self-improvement in production agents is not autonomous self-reflection — it is the transformation of production failures into bounded, verifiable engineering tasks through expert corrections, end-to-end traces, custom eval targets, regression validation, and human review [A+1]. MABW was developed independently and later found to converge with this pattern: human/editor/auditor corrections are structured as Finding Candidates tied to claim IDs, evidence spans, and support labels; only reproducible, classifiable, testable problems enter the improvement queue; and repair is scoped, regressed, and human-approved before release.

---

## 设计原则总结

| v0.9 控制面 | 产业证据来源 | 核心映射 |
|-------------|-------------|---------|
| Atomic Claim Graph | Analytics sub-question alignment [A4], Kepler line-item [A5] | 复合声明 → 原子单元 |
| Evidence Span Registry | Citations API [B4], Kepler provenance [A5] | passage-level → span-level + support label |
| Claim-Support Matrix | Semantic layer [A4], stage-level eval [A5] | 有来源 → 有支持度 |
| Semantic Assessment as Proposal | Generator-verifier criteria [A10], model-as-stage [A5] | LLM judge → proposal layer |
| Human Adjudication Queue | Single-click traceability [A5], Zero Trust human approval [A7] | 全文审核 → 特定声明裁决 |
| Coverage & Omission Gate | Ablation study [A4] | 组件缺失检测 → 维度遗漏检测 |
| Release Eligibility Scorecard | 90% threshold [A4], stage-level eval [A5] | 能发布 → 有资格发布 |
| Quality Pack System | Agent Skills [B3], Plugins [B7] | 自由配置 → 治理工件 |
| Finding Candidate System (v0.9+) | Tax AI production loop [A+1] | 自由反馈 → 结构化发现 → 可验证修复 |

---

## 口径守则

1. **不写**："Anthropic 证明 v0.9 方向正确" → 写："Anthropic 的产业实践提供了行业趋势证据"
2. **不写**："v0.9 已经实现了以上所有能力" → 写："v0.9 路线图定义了这些控制面，实现状态见 §8"
3. **不写**："Citations API = support sufficiency" → 写："Citations 提供 passage-level traceability；v0.9 走到 atom-level support labeling"
4. **不写**："Kepler 证明 MABW 在 briefing 领域有效" → 写："Kepler 在金融领域展示了 deterministic infrastructure + model reasoning 的分离模式"
5. **不写**："Anthropic 的 95% 准确率可以迁移到 MABW" → 写："Anthropic 在其内部分析栈中报告了这些结果"
