# Skills 说明

## market-data-skill

根据公司名称、简称或股票代码自动查询公开行情；也支持用户输入或 seed 行情数据，返回股价、市值、总股本、交易日期和来源。公开接口结果会缓存到 `data/raw/`，需要最新数据时可传入 `refresh=true` 或 CLI `--refresh`。

中文简称优先通过 `config/company_aliases.json` 解析。

## financial-report-skill

根据公司名称、简称或股票代码自动查询公开财务摘要；也支持用户输入或 seed 财务数据，返回收入、净利润、经调整净利润、现金流、现金、债务和多期财务历史等核心指标。

## financial-normalization-skill

把财务数据统一到目标币种和标准单位。1.0 支持 CNY/HKD。

## valuation-skill

确定性估值计算：

- 目标市值倒推股价
- 隐含 PE
- 隐含 PS
- 不同 PE 下达成目标市值所需净利润

## scenario-analysis-skill

输出悲观、中性、乐观三情景。2.0 正式版会基于公司当前净利率动态校准情景利润率，避免所有公司共用同一组固定利润率：

- 收入预测
- 净利润预测
- PE / PS 估值
- 综合市值
- 对应股价

## peer-comparison-skill

2.0 正式版已升级为真实可比公司分析：根据公司名称、简称或 ticker 匹配 `config/peer_groups.json`，批量获取同行公开数据，并计算 PE、PS、净利率、同行中位数、估值定位和每个同行的可比原因。

## research-report-skill

串联核心管线并生成 Markdown 投研报告。直接传入公司名称、简称或股票代码即可自动查找公开数据；也可手工传入 ticker、股本、收入、利润和目标市值覆盖公开数据。

支持：

```json
{"company_name":"腾讯","depth":"deep"}
```

`depth=deep` 会输出深度投研报告，包含可比公司分析、财务质量、增长驱动、风险反证和待验证问题。

可选强制刷新公开数据：

```json
{"company_name":"腾讯","depth":"deep","refresh":true}
```
