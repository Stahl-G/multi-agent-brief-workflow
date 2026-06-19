# Industrial Evidence: Enterprise Agent Harnesses, Verifiable Workflows, and Governance Surfaces

**Purpose**: Draft insertion for MABW Architecture Reference v0.3.0, §10.7
**Created**: 2026-06-19
**Status**: Draft — requires red-team pass before insertion

---

> **关于本节引用。** 本节引用的 Claude/Anthropic 官方文献属于产业实践证据（practitioner evidence / official case study），不构成学术同行评审证明。它们用于支撑以下论点：企业 AI 的前沿实践正在从对话式交互走向可交付、可审计、可治理的 agent 工作流。MABW 的设计与这一趋势一致，但本节不声称这些文献"证明"MABW 的正确性。

---

## 10.7.1 从对话式 AI 到可交付的知识工作 Agent

Anthropic 在 2026 年将 Claude Cowork 定位为"knowledge work agent"：它可以读写本地文件、跨 Slack 和 Google Drive 等连接应用工作、执行多步骤任务，并生成带有实际文件和消息引用的可交付成果（deliverables）[A2]。常见工作流包括 research briefs、meeting prep、recurring reports，输出形式涵盖文档、演示文稿、电子表格和邮件 [A2]。

这一转变的核心不是模型能力的提升，而是任务形态的改变。Anthropic 的最佳实践文档明确区分了 chat 和 Cowork 的适用场景：chat 适用于问答、解释和头脑风暴；Cowork 适用于多输入、多步骤、跨应用、产出文件的任务委派 [A3]。其判断标准有五个维度：多个输入源、产出文件型交付物、重复发生、用户知道什么叫好、中间过程无聊 [A3]。

> "Chat is for when the output is a thought in your head, and Claude Cowork is for when the output is something you'll hand to someone else." [A3]

MABW 的目标交付物——weekly business briefing、management memo、policy tracker、board memo、IR note——恰好符合这一任务形态：多来源输入、结构化输出、重复运行、有质量标准、中间过程（来源检索、声明提取、证据校对）适合委派。

**引用点**：Cowork validates the task shape; MABW addresses the additional problem of claim-level support sufficiency for management briefings.

---

## 10.7.2 企业分析作为上下文与验证问题

Anthropic 在其内部数据分析 agent 的工程实践中得出了一个关键判断：agentic business analytics 的准确性主要是**上下文与验证问题**（context and verification problem），而非单纯的代码生成问题 [A4]。三类主要错误被识别为：

1. **概念/实体歧义**（concept/entity ambiguity）：agent 无法选择正确字段回答用户问题
2. **数据过时**（data staleness）：数据源、业务定义和 schema 持续变化，agent 知识过期
3. **检索失败**（retrieval failure）：正确信息存在于搜索空间中但未被定位 [A4]

Anthropic 的解决路径是：canonical datasets（权威数据集）、sources of truth（四层真相源：语义层、血缘图、查询语料、业务上下文）、freshness/validation（将 skill markdown 与 transformation model 同置，CI hooks 标记无 skill 更新的 schema 变更）、fixed offline eval set（固定评估集，锚定到快照日期或稳定事实表）、ablation（每次只改一个组件比较 pass rate）[A4]。

> "Analytics accuracy is a context and verification problem, not a code generation issue." [A4]

在金融服务领域，Kepler 的实践将这一判断推向了更严格的边界。Kepler 明确将模型放在 pipeline 的一个阶段，而非整个系统："In finance, the model can't be the whole system. We treat it as one stage in a pipeline." [A5]。其架构将确定性基础设施作为信任与验证层，Claude 作为推理与解释层 [A5]。每个数字都需要能追溯到具体 filing、page 和 line item [A5]。技术实现包括：结构化领域知识与硬边界、专有本体（ontology）、确定性执行环境、阶段级评估、完整审计日志和端到端溯源 [A5]。

> "Prompt engineering optimizes a call while content engineering optimizes the system around it." [A5]

MABW v0.9 将同样的分离原则应用到 enterprise briefing 领域：LLM 起草和评估；Python 冻结、验证、通过门禁、记录和投影发布资格。概念定义变成 claim roles；新鲜度变成 source metadata；语义层变成 evidence span registry 和 claim-support matrix；固定评估变成 same-evidence rerun / semantic regression。

**引用点**：Business AI accuracy failures often arise from ambiguous concepts, stale definitions, and retrieval failures; the remedy is governed context, semantic layers, validation, and fixed evals. MABW v0.9 generalizes this from analytics metrics to management-brief claims.

---

## 10.7.3 从 Prompt 到 Harness

Claude Code 在大型代码库中的部署经验揭示了一个关键事实：成功的企业 agent 部署依赖于配置、工具化、所有权、评审流程和治理，而不仅仅是模型能力 [A6]。

Anthropic 识别出五个扩展点构成 harness 层：CLAUDE.md（项目约定）、hooks（自动化一致行为）、skills（领域专业知识打包）、plugins（将配置分发到组织层）、MCP servers（工具和数据连接），以及两个补充能力：LSP integrations 和 subagents（分离探索与编辑）[A6]。

企业部署需要 DRI（Directly Responsible Individual）来维护 settings、permissions policy、plugin marketplace、CLAUDE.md conventions；没有集中化的所有权，"knowledge will stay tribal and adoption will plateau" [A6]。受监管行业需要 approved skills、required code review processes、limited initial access [A6]。

> "Successful enterprise agent deployments depend on configuration, tooling, ownership, review processes, and governance—not only model capability." [A6]

Managed Agents 的实践进一步确认了这一判断。从原型到生产的差距在于基础设施：安全（凭证隔离、prompt injection 防护）、状态管理（持久会话、断点续传）、权限控制（vaults、signed request tokens）、harness 调优（随模型演进适配）[B2]。

> "Infrastructure is what separates a prototype from a production agent." [B2]

Agent Skills 的设计体现了 progressive disclosure 原则：启动时只加载 skill 名称和描述，相关时读取完整 SKILL.md，需要时才访问子文件——保持上下文使用效率 [B3]。但 Skills 也引入安全风险：恶意 skill 可能引入漏洞或引导 agent 泄露数据 [B3]。

MABW 是一个 briefing harness：contracts、control surfaces、gates、frozen artifacts、event logs 和 human approval 扮演的角色，与软件工作流中的 tests、hooks、plugins 和 code review 相同。

**引用点**：MABW is a briefing harness: contracts, control surfaces, gates, frozen artifacts, event logs, and human approval play the same role that tests, hooks, plugins, and code review play in software workflows.

---

## 10.7.4 多智能体系统：适用场景与协调成本

Anthropic 对多智能体系统持审慎态度。其工程文章明确指出，多 agent 只在三种约束下稳定优于单 agent：

1. **上下文污染**（context pollution）：一个子任务的信息对后续子任务无关或有害，subagent 提供干净的隔离上下文
2. **可并行化任务**（parallelizable tasks）：多个 agent 并行探索更大搜索空间
3. **专业化**（specialization）：专注的 toolset 匹配特定职责，避免单 agent 拥有 20+ 工具时的性能退化 [A9]

> "Outside these situations, the coordination costs typically exceed the benefits." [A9]

Anthropic 观察到团队投入数月构建精心设计的多 agent 架构，"only to discover that improved prompting on a single agent achieved equivalent results" [A9]。每个额外的 agent 代表更多故障点、更多需要维护的 prompt、更多意外行为来源。token 成本通常是单 agent 的 3-10 倍 [A9]。

在协调模式层面，generator-verifier 模式只有在评估标准明确时才有效 [A10]。Anthropic 警告：

> "A verifier told only to check whether output is good, with no further criteria, will rubber-stamp." [A10]

团队最常见的失败方式是"implementing the loop without defining what verification means"，这"creates the illusion of quality control without the substance" [A10]。

MABW 的核心不是"多 agent"，而是 contract-backed workflow；多 agent 只是角色隔离和阶段治理的一种执行形态。更重要的是，MABW v0.9 不让 semantic assessor 直接成为真相裁判，而是让它提出 support rows、uncertainty、disagreement，再进入 schema、policy、adjudication 和 release eligibility——这正是 Anthropic 所说的"explicit verification criteria"在 briefing 领域的实现。

**引用点**：Multi-agent systems should be justified by control-path needs, context isolation, parallelization, or specialization—not by aesthetic complexity. Verification loops require explicit criteria; otherwise they create an illusion of quality control.

---

## 10.7.5 从工作流自动化到企业治理

当 agent 接入企业数据和工具时，治理需求从质量控制扩展到安全控制。Anthropic 在 Zero Trust 框架中识别了 agentic 系统的独特风险面：tool access、autonomous decision-making、context persistence、multi-agent coordination，以及当前威胁态势中的 prompt injection、tool poisoning、identity/privilege abuse、memory poisoning、supply chain attacks [A7]。

> "Frontier AI models are compressing the timeline between vulnerability and exploit from months to hours." [A7]

传统访问控制无法阻止 agent 滥用合法权限 [A7]。Anthropic 提出的 Zero Trust 原则是："trust nothing, verify everything, and assume breach has already occurred" [A7]。架构要求包括密码学根身份、任务范围权限、受保护内存和沙箱 [A7]。

在连接器层面，企业 agent 需要集中化的身份、授权和撤销表面 [A8]。MCP 标准化了 agent 如何连接工具和数据，Vaults 处理 OAuth token 管理 [B6]。Skills 和 MCP 互补：MCP 提供工具和数据，Skills 教 agent 如何使用工具完成真实工作 [B6]。

企业管理层需要 SSO、SCIM、审计日志、Compliance API、权限管理、数据留存和使用分析 [B5]。

MABW 的 improvement ledger、human approval、frozen snapshots、event log、delivery gate、connector governance 不仅应被理解为质量控制，也应被理解为企业安全控制。

**引用点**：Autonomous agents require new Zero Trust surfaces: identity, task-scoped permissions, protected memory, sandboxing, and auditability. MABW's control surfaces serve dual purpose: quality governance and enterprise security.

---

## 10.7.6 生产追踪作为自我改进的基底

上述 Claude/Anthropic 文献描述了企业 agent 的任务形态、验证需求、harness 架构和治理框架。但它们没有回答一个关键问题：**agent 系统如何从自己的失败中学习？**

OpenAI 在 2026 年 5 月与 Thrive Holdings 和 Crete 会计师网络共同发布的 Tax AI 案例 [A+1]，提供了目前最完整的生产级回答。Crete 网络包含 30 多家会计师事务所，Tax AI 在报税季处理了 7,000 份报税表，节省约三分之一准备时间，起草准确率最高 97%，吞吐量提升约 50% [A+1]。

但这些数字不是最重要的。最重要的是 OpenAI 围绕三个支柱设计的改进闭环：

1. **专家从业者反馈**（expert practitioner feedback）：会计师在实际使用中修正 agent 的输出
2. **生产追踪**（production tracing）：不只保存输入输出，而是保存从源材料、字段提取及其引用、下游提交，到专家修正的完整路径
3. **Codex 驱动的定制评测迭代**（Codex-driven custom eval iteration）：反复出现的问题被归并成评测目标，再交给 Codex 作为有边界的工程任务 [A+1]

> **自我改进不是 agent 自己反思自己，而是生产系统把失败变成可验证的工程任务。**

OpenAI 明确指出，并非每个从业者修正都会自动变成 Codex 任务。修正可能代表提取遗漏、映射问题、产品不支持、税务判断，或者工作流噪声；只有反复差异经过审查并归并成可执行发现后，才会转成有边界、成功条件明确的任务 [A+1]。

Codex 不是拿一个模糊报错去修改代码，而是拿到一个结构化的任务环境：repo、task.yaml、EXEC_PLAN.md、RESULTS.md、相关产品代码、eval datasets、eval suites、graders、skills、docs、只读 production trace 和 source artifacts [A+1]。

### Tax AI 与 MABW 的结构映射

| Tax AI | MABW 对应物 |
|--------|------------|
| 源文件（source documents） | source pack |
| 字段提取（field extraction） | atomic claim extraction |
| 字段引用（field citations） | evidence span |
| 税务引擎映射（tax engine mapping） | claim-support matrix |
| 从业者修正（practitioner correction） | human adjudication / feedback issue |
| 字段级 review row | support row / finding |
| 重复修正模式（recurring correction pattern） | eval target |
| Codex 修复 PR | scoped MABW workflow repair |
| 回归评测（regression eval） | semantic regression / same-evidence rerun |
| 已提交税表（filed return） | delivered management brief |

### MABW 与 Tax AI 的独立收敛点

MABW 不应该宣传"自进化 agent"。应该说：

> 领导修改、审计发现、引用错配、支持不足，会被转成结构化 finding；只有可复现、可归类、可测试的问题，才进入改进队列。

这与 MABW v0.9 roadmap 的纪律完全一致：v0.9 不是 semantic scoring release，而是从 traceability 到 support sufficiency；semantic model 可以评估、质疑、提出标签，但不能直接决定 release eligibility、claim support truth 或 archive grade。

MABW 的类器官失败研究已经展示了错误传播路径的可追溯性：在直接 LLM 起草中错误通常只留在最终文本里，而在 MABW 中，错误能沿着来源摘要 → 候选声明 → 筛选候选项 → Claim Ledger → 审计简报 → 最终交付回溯。Tax AI 的闭环结构为这种回溯提供了从"发现"到"修复"到"验证"的完整工程路径。

**引用点**：OpenAI's Tax AI case shows that self-improvement in production agents depends on expert corrections, end-to-end product traces, custom eval targets, bounded engineering tasks, regression validation, and human review—not on unbounded autonomous self-reflection. MABW was developed independently and later found to converge with the same production-loop pattern in recurring enterprise briefings: human/editor/auditor corrections are not treated as free-form feedback, but as candidate findings tied to claim IDs, evidence spans, support labels, adjudication state, and release eligibility.

---

## References

### A+-Class (Highest Priority)

- [A+1] OpenAI. "Building Self-Improving Tax Agents with Codex." 2026-05-27. https://openai.com/zh-Hans-CN/index/building-self-improving-tax-agents-with-codex/

### A-Class (Core)

- [A1] Anthropic. "Enterprise AI Category." claude.com/blog/category/enterprise-ai
- [A2] Anthropic. "The Claude Cowork Product Guide." 2026-06-05. claude.com/blog/the-claude-cowork-product-guide
- [A3] Anthropic. "Best Practices for Getting Started with Claude Cowork." 2026-06-03. claude.com/blog/best-practices-for-getting-started-with-claude-cowork
- [A4] Anthropic. "How Anthropic Enables Self-Service Data Analytics with Claude." 2026-06-03. claude.com/blog/how-anthropic-enables-self-service-data-analytics-with-claude
- [A5] Anthropic. "How Kepler Built Verifiable AI for Financial Services with Claude." 2026-04-30. claude.com/blog/how-kepler-built-verifiable-ai-for-financial-services-with-claude
- [A6] Anthropic. "How Claude Code Works in Large Codebases: Best Practices and Where to Start." 2026-05-14. claude.com/blog/how-claude-code-works-in-large-codebases-best-practices-and-where-to-start
- [A7] Anthropic. "Zero Trust for AI Agents." 2026-05-27. claude.com/blog/zero-trust-for-ai-agents
- [A8] Anthropic. "Centrally Manage Authorization for MCP Connectors." 2026-04-22. claude.com/blog/enterprise-managed-auth
- [A9] Anthropic. "Building Multi-Agent Systems: When and How to Use Them." 2026-01-23. claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them
- [A10] Anthropic. "Multi-Agent Coordination Patterns: Five Approaches and When to Use Them." 2026-04-10. claude.com/blog/multi-agent-coordination-patterns

### B-Class (Supplementary)

- [B1] Anthropic. "Claude Managed Agents: Get to Production 10x Faster." 2026-04-08. claude.com/blog/claude-managed-agents
- [B2] Anthropic. "The Evolution of Agentic Surfaces: Building with Claude Managed Agents." 2026-06-10. claude.com/blog/building-with-claude-managed-agents
- [B3] Anthropic. "Equipping Agents for the Real World with Agent Skills." 2025-10-16. anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- [B4] Anthropic. "Introducing Citations on the Anthropic API." 2025-06-23. claude.com/blog/introducing-citations-api
- [B5] Anthropic. "Claude Enterprise, Now Available Self-Serve." 2026-02-12. claude.com/blog/self-serve-enterprise
- [B6] Anthropic. "Building Agents That Reach Production Systems with MCP." 2026-04-22. claude.com/blog/building-agents-that-reach-production-systems-with-mcp
- [B7] Anthropic. "Cowork and Plugins for Teams Across the Enterprise." 2026-02-24. claude.com/blog/cowork-plugins-across-enterprise
