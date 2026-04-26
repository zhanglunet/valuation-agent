# 投研估值 Agent 2.0

这是基于 Hermes Agent + Skills 的上市公司投研估值 Agent。

2.0 版本目标是用户只提供上市公司名称、简称或股票代码，系统自动从公开信息中查找 ticker、行情、市值、股本和财务摘要，并生成任意上市公司的估值与深度投研分析报告，包括：

- 公司基础信息读取
- 公开行情和财务摘要自动获取
- 公开数据本地缓存，可用 `--refresh` 强制刷新
- 币种和单位标准化
- 市值倒推股价
- PE / PS 隐含倍数和所需利润测算
- 基于公司当前利润率校准的三情景估值分析
- 业务分部拆解框架
- 可比公司池、可比原因和同行中位数
- 多期财务趋势、CAGR 和股本变化
- 风险规则、反证测试和待验证问题清单
- Markdown 投研报告生成
- Hermes Skill 包装层

中文简称优先走 `config/company_aliases.json`，未命中时再使用 Yahoo Finance 搜索。别名表可以持续扩充。

## 目录结构

```text
valuation-agent/
├── config/
├── data/
├── docs/
├── skills/
├── tests/
└── valuation_agent/
```

## 文档

- [1.0 设计方案](docs/V1_DESIGN.md)
- [1.0 发布说明](docs/RELEASE_NOTES_v1.0.0.md)
- [安装与导入](docs/INSTALL.md)
- [Skills 说明](docs/SKILLS.md)
- [程序架构](docs/ARCHITECTURE.md)
- [Roadmap](docs/ROADMAP.md)
- [2.0 设计方案与开发计划](docs/V2_DESIGN_AND_DEV_PLAN.md)
- [2.0 正式版设计与开发计划](docs/V2_FINAL_DESIGN_AND_DEV_PLAN.md)
- [2.0 发布说明](docs/RELEASE_NOTES_v2.0.0.md)

## 快速验证

```bash
cd valuation-agent
python3 -m unittest discover -s tests
python3 -m valuation_agent.cli generate-report --query 腾讯
python3 -m valuation_agent.cli generate-report --query 腾讯 --depth deep
python3 -m valuation_agent.cli generate-report --query 腾讯 --depth deep --refresh
```

报告默认输出到：

```text
data/reports/0700_hk_valuation_report.md
data/reports/0700_hk_deep_research_report.md
```

## Hermes Skills 导入

### 通过飞书界面安装

如果 Hermes 已经接入飞书，可以在飞书里直接对 Hermes Bot 发送：

```text
/skills install zhanglunet/valuation-agent --now
```

如果当前 Hermes 部署不支持从 GitHub repo 自动识别多 Skill 目录，可以在飞书里让 Hermes Bot 执行：

```text
请安装 valuation-agent：git clone https://github.com/zhanglunet/valuation-agent.git /tmp/valuation-agent，然后把 /tmp/valuation-agent/skills/* 复制到 ~/.hermes/skills/，最后 /reset 让技能生效。
```

安装后在飞书里验证：

```text
@Hermes 请用 valuation-agent 分析腾讯控股
```

### 通过本地目录导入

方式一：复制到 Hermes 默认目录。

```bash
mkdir -p ~/.hermes/skills
cp -r skills/* ~/.hermes/skills/
```

方式二：在 Hermes 配置中加入当前项目 Skill 路径。

```yaml
skills:
  paths:
    - "~/.hermes/skills"
    - "/Users/john/dev/估值模型/valuation-agent/skills"
```

## Skill 快速调用

```bash
python3 skills/valuation-skill/valuation_skill.py '{"company_name":"腾讯"}'
```

```bash
python3 skills/research-report-skill/research_report_skill.py '{"company_name":"腾讯"}'
```

深度投研报告：

```bash
python3 skills/research-report-skill/research_report_skill.py '{"company_name":"腾讯","depth":"deep"}'
```

## 版本边界

2.0 支持通过 Yahoo Finance 公开接口自动检索上市公司基础行情和财务摘要；用户输入的参数会覆盖公开数据。本地 seed 示例仅用于测试回归。

`--depth deep` 会生成深度投研报告，包含可比公司分析、财务质量、业务分部、增长驱动、风险反证和待验证问题。公开数据可能存在延迟和口径差异，正式研究仍需核验交易所公告、公司年报和最新披露。

本系统仅用于研究分析辅助，不构成投资建议。
