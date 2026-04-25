# 投研估值 Agent 1.0

这是基于 Hermes Agent + Skills 的上市公司投研估值 Agent 第一版实现。

1.0 版本目标是先用用户输入或离线 seed 数据跑通任意上市公司的目标市值测算闭环，包括：

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
python3 -m valuation_agent.cli generate-report \
  --ticker 0700.HK \
  --company-name 腾讯控股 \
  --exchange HKEX \
  --currency HKD \
  --target-market-cap 4000000000000 \
  --shares-outstanding 9500000000 \
  --share-price 420 \
  --revenue 650000000000 \
  --adjusted-net-profit 180000000000
```

报告默认输出到：

```text
data/reports/0700_hk_valuation_report.md
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
@Hermes 请用 valuation-agent 分析 0700.HK：公司名腾讯控股，目标市值 4 万亿港币，总股本 95 亿股，当前股价 420 港币，收入 6500 亿港币，经调整净利润 1800 亿港币。
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
python3 skills/valuation-skill/valuation_skill.py '{"target_market_cap":20000000000,"shares_outstanding":950000000,"revenue":8000000000,"net_profit":800000000}'
```

```bash
python3 skills/research-report-skill/research_report_skill.py '{"ticker":"0700.HK","company_name":"腾讯控股","exchange":"HKEX","currency":"HKD","target_market_cap":4000000000000,"shares_outstanding":9500000000,"share_price":420,"revenue":650000000000,"adjusted_net_profit":180000000000}'
```

## 版本边界

1.0 支持任意上市公司的用户输入参数分析，也保留本地 seed 示例；不自动抓取实时行情。实时公开数据接入放在 1.1。

本系统仅用于研究分析辅助，不构成投资建议。
