# 路线图

这份路线图的目标是保持仓库公开安全、本地优先，同时为更完整的简报生产流程留下扩展空间。

## MVP 已完成

- 支持本地 `.md`、`.txt` 和 `.json` 输入
- Scout 智能体抽取候选事项
- Claim Ledger 记录可追溯的来源化 claim
- Analyst 草稿使用 `[src:CLAIM_ID]` 引用来源
- Deterministic Audit 检查缺失 claim、无支撑数字、重复 claim、脱敏风险和过期来源
- Quality Harness 检查占位符、流程残留文本、低置信来源、陈旧填充内容和单位风险
- 输出 Markdown 简报、事实账本、审计报告和来源映射
- 提供基础 CLI 和 pytest 覆盖

## 近期

- 增加 DOCX 和 PDF 输出，并配套合成示例
- 在公开接口后实现 SEC 和 RSS 连接器
- 增加基于模型的语义审计适配器
- 扩展公开安全示例，包括同行简报和政策简报 demo
- 完善 README、架构说明和 harness 文档
- 增加 GitHub description 和 topics 建议

## 中期

- 增加可复用的行业模块
- 增加面向 management、analyst、IR、strategy 和 policy 受众的角色化模板
- 增加外部分析插件，但所有结论必须先写入 Claim Ledger
- 增加本地语料检索，同时防止 RAG 绕过证据记录
- 按受众和报告类型增加来源分级策略
- 区分 editor 可修复问题和 analyst 阻塞问题

## 长期

- 增加可选的内部消息接入，并配套 allowlist、denylist 和脱敏门控
- 增加结构化指标所需的数据库与语义层适配器
- 为 scout、analyst、audit 和 edit 步骤增加多模型路由
- 增加企业部署模式，并严格处理凭据
- 增加针对过度主张、过期证据和无支撑建议的评估套件

## 安全原则

每一个路线图事项都应该配套公开或合成示例、测试、文档，并且不包含凭据或私有 workflow 产物。
