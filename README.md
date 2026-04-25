# 投研估值 Agent 1.0

这是基于 Hermes Agent + Skills 的上市公司投研估值 Agent 第一版实现。

1.0 版本目标是先用离线 seed 数据跑通亚信科技 `1675.HK` 的 200 亿港币市值目标测算闭环，包括：

- 公司基础信息读取
- 行情和财务 seed 数据读取
- 币种和单位标准化
- 市值倒推股价
- PE / PS 隐含倍数和所需利润测算
- 三情景估值分析
- Markdown 投研报告生成
- Hermes Skill 包装层

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

## 快速验证

```bash
cd valuation-agent
python3 -m unittest discover -s tests
python3 -m valuation_agent.cli generate-report --company asiasoft_1675_hk
```

报告默认输出到：

```text
data/reports/asiasoft_1675_hk_valuation_report.md
```

## Hermes Skills 导入

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
python3 skills/valuation-skill/valuation_skill.py '{"target_market_cap":20000000000,"shares_outstanding":950000000,"revenue":8000000000,"net_profit":800000000}'
```

```bash
python3 skills/research-report-skill/research_report_skill.py '{"company_id":"asiasoft_1675_hk"}'
```

## 版本边界

1.0 使用本地 seed 数据，不自动抓取实时行情。实时公开数据接入放在 1.1。

本系统仅用于研究分析辅助，不构成投资建议。
