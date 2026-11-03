# Hi, I'm Miro（陈颖） 👋

**AI 全栈工程师 · Agent Harness · 上下文工程**

8 年前端及全栈开发经验，做过桌面智能体、电商家居 Agent、GEO 多平台采集系统与内部协作工具。关注从交互、Agent 编排到后端服务的完整产品交付，独立设计开发开源项目 **[Inalpha](https://github.com/mirror29/inalpha)**。

*AI full-stack engineer with 8 years of frontend and full-stack experience. I build AI products and explore agent orchestration, context engineering, and controlled execution through Inalpha.*

[Inalpha 网站](https://inalpha.dev) · [邮箱](mailto:926320181@qq.com) · [LinkedIn](https://www.linkedin.com/in/miro-chen-467023301)

## 我关注的工程问题

- **Agent Harness：**实践工具编排、权限审批、受限代码执行、人工接管与任务恢复；使用过 PI Agent、OpenAI Agents SDK 和 Mastra。
- **上下文工程：**RAG 知识检索、Skill 按需加载与任务上下文组织，让工具和信息围绕当前任务工作。
- **AI 产品交付：**连接 Web / Electron 客户端、流式交互、可编辑画布与后端服务，推进需求梳理、实现和部署。
- **工程化与质量：**组件库、Monorepo、构建与运行时性能优化，结合接口契约校验、自动化测试、执行追踪和 Sentry 定位问题。

## 🦊 Inalpha

**个人独立设计开发的开源量化实验框架。** 将多 Agent 研究、因子分析、策略生成、回测和模拟盘连接为可追踪的实验流程。

[源码](https://github.com/mirror29/inalpha) · [项目网站](https://inalpha.dev) · [中文文档](https://github.com/mirror29/inalpha/blob/main/README.zh-CN.md)

### 研究与全栈交互

以 Next.js 控制台连接 Mastra 编排层和 Python 服务，支持多视角研究与多空讨论，记录研究证据、分歧和决策过程；结合因子血缘、衰减巡检及回测结果支持复盘。

### Agent Loop 与进化系统

```text
冻结数据与预算 → 生成研究假设 → 确定性编译候选策略 → 回测评估
                       ↑                              │
                       └──────── 评估反馈驱动迭代 ─────┘
                                      │
                                      ↓
                        冠军候选 → Forward / Holdout → 人工采用
```

围绕实验循环设计持久化状态、检查点、重复触发复用与租约恢复机制，使迭代过程能够追踪和恢复。实验性采用与模拟盘执行分开控制，不因产生候选结果就自动启动策略或下单。

### Harness 与执行边界

为模型生成代码设置审计、受限执行与接口校验；通过 propose → approve → execute 链路、一次性限时审批令牌和决策日志控制敏感操作。结合时序交叉验证与统计校正降低回测过拟合风险。

> 项目持续迭代中。进化系统的完整正向生产验收仍待完成；已实现能力与验证状态见[项目状态文档](https://github.com/mirror29/inalpha/blob/main/docs/04-current-state.md)。

## 其他项目与产品经历

| 项目 / 方向 | 我的工作 |
| --- | --- |
| **[OpenFinClaw CLI](https://github.com/mirror29/openfinclaw-cli)** | 开源工具开发：TypeScript CLI 与 MCP Server 双入口，已发布 npm 包 `@openfinclaw/cli`，提供交互式安装向导。 |
| **[电商家居 Agent / Owlume](https://www.owlume.work/)** | 在新旦相关经历中担任项目负责人，推进需求、技术选型与开发协作；使用 OpenAI Agents SDK / FastAPI，连接 Next.js、CopilotKit / AG-UI 与 Tldraw 画布交互。 |
| **桌面智能体** | 在熵基律动负责 Electron 客户端开发，使用 PI Agent 进行编排，实践 Skill 管理、会话隔离、人工接管与任务恢复。 |
| **GEO 与内部提效** | 开发多平台 AI 答案及引用采集系统；建设飞书协作助手，串联需求、缺陷、源码分析与研发日报。 |
| **[wangEditor-formula](https://github.com/mirror29/wangEditor-formula)** | 公式编辑器插件，集成 kityformula 与 myscript-math-web，保留前端编辑器扩展方面的实践。 |

## 常用技术

| 方向 | 技术 |
| --- | --- |
| 前端与客户端 | TypeScript · React · Next.js · Vue · Electron · Tldraw |
| Agent 与交互 | PI Agent · OpenAI Agents SDK · Mastra · MCP · CopilotKit · AG-UI |
| 后端与数据 | Python · FastAPI · Node.js · PostgreSQL · pgvector |
| 工程与质量 | Monorepo · CI/CD · Docker · Vitest · Playwright · Sentry |

## 联系我

欢迎交流 AI 产品、Agent 工程与全栈开发机会。

**[926320181@qq.com](mailto:926320181@qq.com)** · [inalpha.dev](https://inalpha.dev)

---

*做个梦给你 · Building Inalpha 🦊*
