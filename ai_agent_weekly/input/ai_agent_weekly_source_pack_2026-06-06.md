# AI大模型和AGENT行业周报 source pack

生成日期：2026-06-06
来源窗口：2026-05-23 至 2026-06-06
用途：为 `multi-agent-brief prepare` 提供公开、可引用、带日期的候选信息。以下内容均为公开来源摘要，不包含内部信息。

## 候选信息

1. OpenAI 于 2026-06-02 发布 “Codex for every role, tool, and workflow”，宣布面向不同岗位的 Codex 插件、Sites 和 annotations。官方称 Codex 周活用户超过 500 万，非开发者用户约占 20%，且增长速度超过开发者群体。管理启示：Codex 正从代码助手扩展为通用知识工作 Agent 平台，企业落地方向从 IDE 进入分析、销售、设计、投研等业务岗位。来源：OpenAI，2026-06-02，https://openai.com/index/codex-for-every-role-tool-workflow/

2. OpenAI 在同一发布中称，六个岗位插件覆盖数据分析、创意生产、销售、产品设计、公开股票投资、投行等角色；每个插件打包相关 apps、skills、instructions 和 workflows。管理启示：Agent 产品竞争正在从“模型能力”转向“角色工作流封装 + 工具生态连接”。来源：OpenAI，2026-06-02，https://openai.com/index/codex-for-every-role-tool-workflow/

3. OpenAI ChatGPT release notes 于 2026-06-04 更新，提到 ChatGPT memory 更自动地保持上下文更新，并带有基础设施改进；同时宣布 ChatGPT 中 OpenAI o3 将于 2026-08-26 退役，GPT-4.5 将于 2026-06-27 退役。管理启示：旧模型退役周期压缩，团队如果依赖指定模型，需要建立模型替换和回归测试机制。来源：OpenAI Help Center，2026-06-04，https://help.openai.com/en/articles/6825453-chatgpt-release-notes

4. OpenAI release notes 在 2026-05-21 记录 Codex 更新：Appshots、Goal mode、浏览器 annotations、remote locked use 和浏览器能力改进。管理启示：长任务 Agent 的关键产品能力包括上下文捕获、目标模式、浏览器交互、远程持续执行和可审查进度，而不仅是模型推理能力。来源：OpenAI Help Center，2026-05-21，https://help.openai.com/en/articles/6825453-chatgpt-release-notes

5. Anthropic 于 2026-05-28 发布 Claude Opus 4.8，定位为更强的 coding、agentic tasks 和 professional work 模型，并称 fast mode 速度可达此前 2.5 倍、成本较此前 fast mode 降低。管理启示：Claude 继续把长程 coding/agent 工作作为旗舰模型卖点，价格和速度成为企业 adoption 的重要变量。来源：Anthropic，2026-05-28，https://www.anthropic.com/news/claude-opus-4-8

6. Anthropic 对 Opus 4.8 的介绍强调其在长任务中更会标记不确定性，减少缺乏证据的进展声明。管理启示：Agent 评估应把“诚实报告不确定性”和“避免虚假完成”纳入验收，而不是只看任务完成率。来源：Anthropic，2026-05-28，https://www.anthropic.com/news/claude-opus-4-8

7. Anthropic Institute 文章 “When AI builds itself” 披露，截至 2026-05，Anthropic 合并到代码库中的代码超过 80% 由 Claude 编写；2026 年二季度典型工程师每日合并代码量约为 2024 年的 8 倍。管理启示：AI coding agent 已进入自家研发闭环验证阶段，但应注意该数据来自 Anthropic 自述，适合视作供应商侧证据。来源：Anthropic Institute，抓取于 2026-06-05/06，https://www.anthropic.com/institute/recursive-self-improvement

8. 同一 Anthropic Institute 文章称，Claude 在开放式 Claude Code 任务上的成功率在 2026-05 达到 76%，六个月内提升 50 个百分点。管理启示：长程任务能力上升速度很快，管理层需要重新评估“Agent 可独立承担的任务边界”和人工 review 节点。来源：Anthropic Institute，抓取于 2026-06-05/06，https://www.anthropic.com/institute/recursive-self-improvement

9. Google 于 2026-06-05 汇总 5 月 AI 更新，称 Gemini 3.5 系列面向复杂多步 agentic workflows，并强调 Gemini app 的 proactive helper 能力。管理启示：Google 将 Agent 从开发者平台推进到消费端和工作流入口，重点是跨 app 的持续执行。来源：Google Blog，2026-06-05，https://blog.google/innovation-and-ai/technology/ai/google-ai-updates-may-2026/

10. Google I/O 2026 汇总称 Gemini Spark 是 24/7 personal AI agent，Daily Brief 是面向个人日程/邮件/任务的 out-of-box agent，且 Daily Brief 面向美国 Google AI 订阅用户推出。管理启示：日程、邮件、任务摘要是个人 Agent 的首批高频场景，对小米端侧/系统级 AI 助理体验有参考价值。来源：Google Blog，2026-05-20，https://blog.google/innovation-and-ai/technology/ai/google-io-2026-all-our-announcements/

11. Google Cloud 于 2026-04-22 宣布 Gemini Enterprise Agent Platform，用于构建、扩展、治理和优化 Agent，并与 Vertex AI、数据、安全能力整合。管理启示：企业 Agent 平台竞争重点转向治理、DevOps、安全与模型/工具集成。来源：Google Blog，2026-04-22，https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/gemini-enterprise-agent-platform/

12. Reuters 报道，Meta 于 2026-06-03 发布面向企业日常运营的 AI business agent，进入企业 AI agent 市场。管理启示：Meta 可能从社交/广告/商业消息入口切入企业 Agent，值得关注其在企业运营和商业账号场景的后续扩展。来源：Reuters via Investing.com，2026-06-03，https://www.investing.com/news/stock-market-news/meta-launches-enterprisefocused-ai-business-agent-to-automate-daily-operations-4724559

13. 新浪科技 2026-06-02 报道，豆包预计 6 月下旬上线付费内容；文中引用 QuestMobile 数据称 2026 年一季度豆包 DAU 约 1.4 亿、MAU 约 3.45 亿，并援引火山引擎披露称 2026 年 3 月豆包大模型日均 token 使用量超过 120 万亿。管理启示：国内 C 端大模型进入商业化与算力成本压力显性化阶段。来源：新浪科技，2026-06-02，https://finance.sina.com.cn/tech/roll/2026-06-02/doc-inhzzqcn4736837.shtml

14. 36氪 2026-06-04 报道，字节 AI 的四个关键命题包括世界模型、Seedance、Coding 和豆包商业化，其中 Coding 方向强调 dogfooding 和提升 Agent 能力，豆包商业化重点场景为办公。管理启示：字节的 Agent 重点可能从通用聊天向办公与 coding 生产力转移。来源：36氪，2026-06-04，https://www.36kr.com/newsflashes/3838463320869128

15. 月之暗面于 2026-06-03 宣布 Kimi Work 开启公测；报道称其面向知识工作者，能够拆解任务、并行执行、调用工具、使用浏览器并交付文档、表格、PPT 等产物。管理启示：国内 Agent 形态正在从在线聊天和 coding agent 走向本地桌面 working agent。来源：智通财经 via Investing.com，2026-06-04，https://hk.investing.com/news/stock-market-news/article-1493853

16. Kimi Work 报道称其支持 Agent 集群，最高可根据任务复杂度自主创建 300 个子 Agent。管理启示：多 Agent 编排正在成为国产 Agent 产品的显性卖点，但需要重点验证实际稳定性、成本和可控性。来源：智通财经 via Investing.com，2026-06-04，https://hk.investing.com/news/stock-market-news/article-1493853

17. Alibaba Cloud Community 2026-05-28 报道，Alibaba Cloud 面向全球市场推出 Qwen Cloud，并称其为 AI Agents 而生；文章提到 Agent 爆发正在推动模型调用和云资源消耗增长。管理启示：阿里正在把 Qwen 从模型品牌扩展到 Agent-native 云平台，与云资源消费和国际化绑定。来源：Alibaba Cloud Community，2026-05-28，https://www.alibabacloud.com/blog/alibaba-cloud-launches-qwen-cloud-for-global-markets_603191

18. Alibaba Cloud 2026-04-02 发布 Qwen3.6-Plus，强调 agentic coding、多模态感知和推理，并将其集成进 Wukong 多 Agent 企业平台和 Qwen App。管理启示：阿里路线是模型升级 + 企业多 Agent 平台 + 消费端应用的组合。来源：Alibaba Cloud，2026-04-02，https://www.alibabacloud.com/en/press-room/alibaba-unveils-qwen3-6-plus-to-accelerate-agentic

19. 智谱开放平台页面显示 GLM-5.1 定位为新旗舰模型，强调 Coding、智能体、数理推理、PPT 生成等能力，并称长程任务和 coding 能力增强，适合作为 Autonomous Agent 与长程 Coding Agent 基座。管理启示：国产基础模型厂商正在把长程执行、文档生产和 coding agent 作为主战场之一。来源：智谱 AI 开放平台，抓取于 2026-06-05/06，https://open.bigmodel.cn/

20. Cisco 于 2026-06-02 发布 Cisco Cloud Control，称其是面向 humans and AI agents 管理、监控和防御关键 IT 基础设施的统一平台。管理启示：Agent 上线后，基础设施、可观测性、安全和 tokenomics 将成为企业治理重点。来源：Cisco Newsroom，2026-06-02，https://newsroom.cisco.com/c/r/newsroom/en/us/a/y2026/m06/cisco-unveils-agentic-platform-for-operating-and-defending-critical-it-infrastructure.html

21. Noma 于 2026-06-02 发布 Agentic Access Control，用于发现、治理并执行 AI agents 和 MCP servers 的访问策略。管理启示：MCP/工具调用扩散后，Agent 权限治理将成为企业安全刚需。来源：PR Newswire，2026-06-02，https://www.prnewswire.com/news-releases/noma-launches-agentic-access-control-to-govern-ai-agents-and-mcp-servers-across-the-enterprise-302788534.html

22. MoEngage 于 2026-06-03 发布 Merlin AI Custom Agents，强调可见性、guardrails 和 Open MCP Architecture，并向 Claude/ChatGPT 等外部工具开放 MCP server。管理启示：业务 SaaS 厂商正在把自身数据和动作能力包装为 Agent/MCP 可调用接口。来源：PR Newswire，2026-06-03，https://www.prnewswire.com/news-releases/moengage-launches-merlin-ai-custom-agents-with-full-visibility-marketer-defined-guardrails-and-open-mcp-architecture-302789285.html

23. Futurum Group 2026-06-01 报告称，AWS、Google 等云厂商正在围绕 agent orchestration runtime、enterprise agent platform 和 agentic data cloud 等方向竞争。管理启示：Agent 平台竞争不会只发生在模型层，云平台和数据层会定义企业接入门槛。来源：Futurum Group，2026-06-01，https://futurumgroup.com/press-release/agentic-ai-the-leading-vendors-winning-the-enterprise-in-2026/

24. Microsoft Build 2026 相关报道显示，Microsoft 发布 Scout agent 和 MAI-Thinking-1，并强调 Autopilots 等长程企业 Agent。管理启示：虽然不在本次重点竞对名单中，但微软在 Office、Copilot、GitHub 和企业租户中的 Agent 化进展会直接影响 OpenAI 生态和企业工作流预期。来源：Axios，2026-06-02，https://www.axios.com/2026/06/02/microsoft-debuts-scout-agent-homegrown-reasoning-model

## 使用注意

- 媒体来源中的未证实数字或“据悉/知情人士”信息，应在成稿中标注为媒体报道，不应写成已被公司确认的事实。
- Anthropic、OpenAI、Google、Alibaba、Cisco、Noma、MoEngage 等官方来源可以作为较高可信度来源，但仍需区分产品发布、供应商自评和第三方评测。
- 涉及竞对能力对比时，不应只引用厂商自述 benchmark；需要在后续版本中增加独立评测或真实使用评估。
