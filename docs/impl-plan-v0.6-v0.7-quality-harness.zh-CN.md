# v0.6 / v0.7 Quality Harness Plan

本计划把 v0.6 和 v0.7 定义为质量主线：目标不是让模型“凭自觉变聪明”，而是把管理层周报的质量要求工程化为 contract、gate、artifact 和 regression test。

```text
v0.6: 定义意图、相关性和交付门槛，防止差稿交付
v0.7: 引入总编辑综合层，提高好稿稳定产出
```

MABW 的长期方向是：代码负责事实、结构和门禁；模型负责受控的语义判断和编辑表达；最终交付必须经过可审计质量门。

## v0.5.x 前置收敛

v0.6 之前先收敛三个前置能力，避免质量主线建立在不稳定交付物上。

### v0.5.2 Finalize / Reader-Facing Artifact

- `audited_brief.md` 保留 `[src:CLAIM_ID]`，作为审计文本。
- `brief.md`、自动命名 Markdown、DOCX 清除 `[src:CLAIM_ID]`，作为 reader-facing 交付物。
- `finalize` 成为正式交付阶段，而不是可选格式化动作。
- Demo smoke 不得出现 0 claims。
- DOCX smoke 必须生成 `brief.docx`。
- Reader-facing artifact 必须可打开、可渲染、无过程残留。

### v0.5.3 Epistemic Presentation / AnalysisBlocks

新增最小 `AnalysisBlock`：

```yaml
AnalysisBlock:
  block_id
  title
  fact_claim_ids
  interpretation_claim_ids
  limitation_claim_ids
  to_verify_claim_ids
  relevance_score
  applicability_note
  verification_path
```

硬规则：

- 假设不能写成事实。
- 类比和案例必须说明适用边界。
- 没有证据的行动建议降级为 `to_verify`。
- 重要事项必须有事实支撑，或显式暴露证据缺口。

### v0.5.4 Input Classification & Feedback Hygiene

输入进入 pipeline 前先分类：

- source evidence
- user instruction
- feedback / revision request
- agent process residue
- config / setup text
- report content

硬规则：

- 用户反馈不是新闻来源。
- Agent 过程文本不是 reader-facing 报告内容。
- source gap、research gap 和 next-step note 不能混进正文事实叙述。

## v0.6: Intent & Delivery Quality Gate

目标：系统必须知道报告写给谁、写什么、哪些信息相关、什么结构才算可交付，并能阻断明显坏稿。

### v0.6.0 BriefIntentContract

新增：

```text
src/multi_agent_brief/intent/
  schemas.py
  resolver.py
  validators.py
```

核心对象：

```yaml
BriefIntent:
  language
  audience
  audience_profile
  topic
  primary_question
  target_entities
  required_sections
  banned_sections
  required_perspectives
  source_priority
  output_tone
  delivery_format
  industry_pack_id
```

AI / Agent 行业周报示例：

```yaml
language: zh-CN
audience: 小米大模型团队管理层
topic: AI 大模型与 Agent 行业周报
target_entities:
  - 小米
  - OpenAI
  - Anthropic
  - Google / Gemini
  - 国内大模型
  - Coding Agent
  - MCP / Tool Use
required_sections:
  - 执行摘要
  - 本周最重要变化排序
  - 重点厂商动态
  - 对目标团队的观察维度
  - 风险与不确定性
  - 下周跟踪清单
  - 来源清单
banned_sections:
  - Policy
  - Earnings
  - Competitor
```

输出：

```text
output/intermediate/brief_intent.json
```

注意：`banned_sections` 是 intent-specific 约束，不是全局禁用词。

### v0.6.1 Industry Intent Packs MVP

先支持少量行业意图包：

- `manufacturing_industrial`
- `finance_investment`
- `internet_ai_agent`
- `soe_industrial_group`
- `public_sector_policy`

每个 pack 定义：

- `required_sections`
- `optional_sections`
- `banned_sections`
- `source_priority`
- `relevance_rules`
- `must_preserve_facts`
- `tone_rules`
- `delivery_gate_overrides`

示例方向：

- 制造业：供应链、产能、客户、质量、法规、成本与交付风险。
- 金融投资：事件、数字、假设、估值口径、风险、不确定性和信息披露边界。
- AI / Agent：模型、产品、Agent 能力、工具调用、企业治理、安全、关键厂商动态。
- 国企产业集团：政策、产业链、合规、投资建设、供应安全、经营风险。
- 公共部门：政策来源、执行状态、影响范围、公众风险、后续节点。

### v0.6.2 RelevanceGate

新增：

```text
src/multi_agent_brief/relevance/
  schemas.py
  scorer.py
  policy.py
  report.py
```

核心原则：

```text
RelevanceGate 是 LLM-assisted, code-enforced relevance gate。
语义判断可以由 LLM / heuristic 提出，最终门槛由代码裁决。
```

核心对象：

```yaml
ClaimRelevance:
  claim_id
  topic_relevance: 0-3
  audience_relevance: 0-3
  target_entity_relevance: 0-3
  time_relevance: 0-3
  actionability: 0-3
  evidence_strength: 0-3
  rationale
  reviewer: rule | llm | hybrid
  recommended_use: executive_summary | main_body | appendix | background | drop | to_verify
  blocking_reasons
```

Scorer 拆分：

- `RuleBasedRelevanceScorer`
- `LLMRelevanceScorer`
- `HybridRelevanceScorer`

代码可判定的部分：

- 是否命中目标实体或主题关键词。
- 是否落在 report window。
- 来源类型、来源层级、是否 stale。
- Claim epistemic type 和 evidence relation。
- 是否官方来源、媒体报道、研究/安全报告、社区信号、供应商自述。

模型适合参与的部分：

- 为什么这条信息对目标读者重要。
- 这条信息与主题/目标组织的关系是什么。
- 应进入 executive summary、main body、background 还是 appendix。
- 是否应降级为 `to_verify`。

门槛由代码执行：

```python
if topic_relevance == 0:
    recommended_use = "drop"
if audience_relevance == 0:
    recommended_use = "appendix"
if time_relevance == 0:
    recommended_use = "background"
if evidence_strength <= 1 and actionability >= 2:
    recommended_use = "to_verify"
if recommended_use == "drop" and claim_id in final_markdown:
    audit_fail()
```

输出：

```text
output/intermediate/relevance_report.json
```

完成标准：

- 明显无关 claim 不进入正文。
- 弱相关 claim 只能进入 appendix / background，不能进入执行摘要。
- `drop` claim 被最终正文引用时 audit fail。
- AI / Agent 周报中，医学 AI 论文、能源 AI 营销、法律 AI PR 等无法解释与目标读者关系的内容必须 drop 或降级。

### v0.6.3 DeliveryQualityGate MVP

扩展：

```text
src/multi_agent_brief/audit/final_quality.py
```

检查项：

- `language_match`
- `intent_section_coverage`
- `target_entity_density`
- `generic_template_leakage`
- `executive_summary_presence`
- `source_stratification_presence`
- `reader_specific_perspective`
- `tracking_list_presence`
- `risk_section_presence`
- `prepare_draft_leakage`
- `reader_src_leakage`

硬失败：

- Reader-facing 文本出现 `[src:`。
- 标题或正文出现 `Generated Brief` 这类 prepare draft 痕迹。
- 缺执行摘要。
- 缺风险与不确定性。
- 缺下周跟踪清单。
- 缺 intent 要求的核心章节。
- 出现 intent 禁用章节。
- 中文报告中文占比过低。
- AI / Agent 周报没有 OpenAI / Anthropic / Agent 等核心结构。
- 管理层报告没有目标组织或目标团队观察维度。

Warnings：

- target entity density 偏低。
- source stratification 弱。
- 摘要过长或过短。
- claim utilization 过低。
- background 占比过高。
- 供应商自述没有充分标注。

输出：

```text
output/intermediate/delivery_quality_report.json
```

完成标准：

- `Generated Brief` + `Policy / Earnings / Competitor` 这类通用模板稿会失败。
- Reader-facing `[src:CLAIM_ID]` 泄漏会失败。
- 结构完整但来源分层弱的稿件给 warning。
- 严重等级可以被 Industry Pack 覆盖，但默认不能弱化核心交付门。

## v0.7: Executive Synthesis Reliability

目标：不只拦差稿，还要把“总编辑综合层”变成稳定阶段，让免费模型或弱模型在受控任务中也能产生可交付初稿。

### v0.7.0 ExecutiveSynthesizer

新增：

```text
src/multi_agent_brief/synthesis/
  planner.py
  executive_frame.py
  section_writer.py
  editor_pass.py
  renderer.py
```

输入：

- `brief_intent.json`
- `claim_ledger.json`
- `relevance_report.json`
- `analysis_blocks.json`
- `source_map.md`
- `source_coverage_report.json`
- optional `previous_report.md`

输出：

- `executive_frame.json`
- `section_drafts/`
- `synthesized_brief.md`

推荐流程：

```text
claims
→ relevance_report
→ analysis_blocks
→ executive_frame
→ section drafts
→ editor pass
→ synthesized_brief
→ delivery_quality_gate
```

核心对象：

```yaml
ExecutiveFrame:
  top_developments
  entity_sections
  theme_sections
  target_company_observation_dimensions
  risks_and_uncertainties
  next_week_tracking
  source_stratification
  excluded_or_deprioritized_items
```

模型只做受控小任务：

- 对 5-10 条候选 claim 排序。
- 为一个 AnalysisBlock 写 120-200 字解释。
- 说明“为什么重要”。
- 把 limitation 改写为 verification path。
- 把 vendor self-claim 降级为供应商表述。
- 统一中文管理层语气。

禁止：

- 模型直接联网补事实。
- 添加 ledger 外事实。
- 把 hypothesis / to_verify 写成事实。
- 把“管理层可观察”写成“公司应执行”。

完成标准：

- `synthesized_brief.md` 比 deterministic draft 更像管理层周报。
- 关键事实仍可追溯到 Claim Ledger。
- DeliveryQualityGate 在 synthesis 后运行。
- Synthesizer 失败时不得 fallback 到 deterministic draft 直接交付，必须 fail 或 human review。

### v0.7.1 Source Stratification & Evidence Boundary

引入来源分层：

```yaml
source_stratification:
  official_confirmed
  company_disclosure
  trusted_media
  research_or_security
  community_signal
  vendor_claim
  unverified_or_to_verify
```

边界规则：

- 供应商自述不是第三方事实。
- 媒体报道必须写成媒体报道。
- 社区信号不能单独支撑核心结论，除非另有来源支持。
- 安全研究应保留研究边界和复现限制。
- 管理层判断必须同时呈现事实、解释和不确定性。

### v0.7.2 Golden Sample Harness

不提交真实 DOCX，使用 public-safe synthetic fixtures：

```text
examples/golden_quality/
  good_executive_brief/
  bad_template_leak/
  weak_but_acceptable/
  ai_agent_weekly/
  manufacturing_quiet_week/
  finance_conflicting_sources/
```

期望：

- good sample pass。
- bad sample fail。
- weak sample warning。

指标：

- `language_ratio`
- `required_section_coverage`
- `target_entity_density`
- `source_layer_count`
- `claim_utilization_rate`
- `template_leak_score`
- `risk_section_score`
- `tracking_section_score`
- `executive_summary_score`
- `reader_src_leak`

完成标准：

- 类似 prepare-only 的 `Generated Brief / Policy / Earnings / Competitor` 稿件失败。
- 类似人工总编辑综合后的管理层稿件通过或仅有轻微 warning。
- 来源分层强的审计型样例作为 baseline 通过。
- 同一 harness 可跨 runtime / model 复用。

### v0.7.3 Cross-Runtime Quality Regression

比较同一任务、同一来源、同一 intent 在不同 runtime/model 下的结果：

- Codex + GPT
- Claude Code + MiMo
- OpenCode + DeepSeek / MiMo

记录：

- `delivery_quality_status`
- section coverage
- template leakage
- source stratification
- executive summary score
- target entity density
- reader `[src]` leakage
- claim utilization

目标：

- 强模型应通过质量门。
- 弱模型至少不能硬交付坏稿。
- 弱模型可以产出 editable draft，但不能被标为 delivery-ready。
- runtime/model 差异进入 regression report，而不是靠人工感觉判断。

## v0.8 / v2.0 前置：Event Completeness MVP

Event Completeness 不进入 v0.6 / v0.7 主线，可作为 v0.8 或 v2.0 前置实验。

候选事件族：

- M&A
- 融资
- IPO
- 重大投资
- 技术发布
- 诉讼 / 专利
- 监管

字段检查：

- amount
- date
- location
- actors
- object
- stage
- source
- undisclosed fields

缺失状态：

- `not_found`
- `not_disclosed`
- `not_verified`
- `conflicting`
- `not_applicable`

只允许一轮 bounded Missing-Fact Search，不能干扰 v0.6 / v0.7 的质量主线。

## 与 v2.0 MAS Runtime 的关系

v0.6 / v0.7 是质量地基，不替代 v2.0。

它们回答：

- 什么是好周报。
- 什么是 off-topic。
- 什么是管理层可读。
- 什么信息够相关。
- 什么来源分层才可交付。

v2.0 回答：

- 多 Agent 如何协作。
- 状态如何共享。
- 过程如何 replay。
- 多模型、多 runtime 如何治理。

未来 Shared World 应把以下对象作为 contract / artifact / event payload，而不是硬编码在某个 runtime 内：

- `BriefIntent`
- `IndustryPack`
- `RelevanceAssessment`
- `AnalysisBlock`
- `ExecutiveFrame`
- `DeliveryQualityReport`

## 版本边界

v0.6 必须完成：

- Intent Contract
- Industry Packs MVP
- Relevance Gate
- Delivery Quality Gate

目标：明显坏稿不能交付。

v0.7 必须完成：

- Executive Synthesizer
- Source Stratification
- Golden Sample Harness
- Cross-Runtime Regression

目标：稳定产出管理层可读的高质量周报。

暂缓：

- v0.6 不做 Event Completeness。
- v0.7 不做 DOCX 渲染大重写。
- v0.7 不做 MAS Runtime。
- 不做 one-shot model full brief。
- 不把 Industry Pack 硬编码成 runtime 逻辑。
- 不允许弱模型输出直接作为正式交付。
