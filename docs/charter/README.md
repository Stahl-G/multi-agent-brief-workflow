# MABW Charter

This charter defines the architecture and operating disciplines for Multi-Agent
Brief Workflow. It is written in Chinese because it originated from the
project's internal architecture rulings. Public capability claims still depend
on implemented code, tests, docs, and the support matrix.

## MABW Architecture Charters

### 1. 聪明的无权，有权的确定，生效的过人，过人的留痕。

LLM / agent 可以理解、建议、拆分、起草，但不能直接生效；真正写状态、推进流程、冻结证据、通过门禁的，必须是确定性控制面。任何影响后续运行的东西都要人类确认，并留下记录。

### 2. 机器能管的，不交给记忆。

schema、validator、gate、transaction、event log 这些机器强制的部分可靠；只写在 prompt、handoff、口头规则里的东西，在真实 run 里迟早会漂移。凡是能被确定性检查捕获的规则，就不应停留在 guidance。

### 3. 同一个字段只许有一个写者。

每个控制面字段必须有唯一权威写入方。Python 写状态、账本、事件、哈希、门禁；LLM 写内容草稿；人类批准偏好和最终交付。多个模块“顺手更新”同一字段，会破坏审计、回滚和归因。

### 4. 有来源，不等于被支持；能追溯，不等于被证明。

一条来源记录只证明某个 claim 在何时、从何处、经由哪一步进入流程；它不自动证明该来源在语义上支持这个 claim。检索计划、source candidates、模型摘要、搜索摘要只能作为发现线索，不能作为事实证据。证据支持必须按强度、来源层级和新鲜度分开记录；新鲜不等于权威，有链接不等于被证明。

### 5. 冻住的不许改；要变就新增，要坏就标脏。

一件 artifact 一旦被确定性控制面冻结，就不能被静默覆盖。合法变化必须表现为新的 revision、新的 artifact、新的 event，或显式的 supersede / revert / contamination 记录；不能把旧冻结物原地改写成“好像一直如此”。同一字段的唯一写者也不能回头改写已经冻结的历史。

### 6. 冲突按层级，不按聪明。

当用户请求、agent 建议、audience preference、improvement memory、repair plan、gate、schema、contract 彼此冲突时，系统不靠模型解释谁更合理，而靠预先声明的 precedence 决定谁赢。事实契约和确定性 gate 高于风格偏好；本 run 的 repair 高于跨 run 的 taste memory；控制面义务不被 prompt、handoff 或用户临时请求覆盖。

## MABW Operating Disciplines

### Product Spine: 加速不偷问责。

MABW 可以通过复用冻结证据、减少重复推理、改善引导路径、并行非依赖工作来变快；但不能通过减少 ledger、gate、人类确认、event、snapshot、archive 来变快。轻量化只能轻外壳，不能抽脊柱。

### Public Claims Discipline: 不说 artifact 支撑不了的话。

MABW 的公开文档、README、release note、demo、论文草稿和推广帖，不能宣称超过当前 artifacts 能证明的能力。未测量就写 NOT MEASURED；只能追溯就说 traceability；不能把人工核查发现的错误包装成模型自证；失败案例如果影响能力边界，应作为系统证据的一部分公开。

### Data Boundary: 私有事实不为公共机制背书。

MABW 可以从真实工作流中蒸馏模式、失败类型、控制面规则和测试形态，但私有业务事实、客户事实、雇主材料、IR 内容、未公开信息不得进入 repo、fixtures、公开 demo 或未批准的外部 API。公共机制必须能用公开语料或合成材料复现。
