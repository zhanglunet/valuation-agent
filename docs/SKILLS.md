# Skills 说明

## market-data-skill

读取 seed 行情数据，返回股价、市值、总股本、交易日期和来源。

## financial-report-skill

读取 seed 财务数据，返回收入、净利润、经调整净利润等核心指标。

## financial-normalization-skill

把财务数据统一到目标币种和标准单位。1.0 支持 CNY/HKD。

## valuation-skill

确定性估值计算：

- 目标市值倒推股价
- 隐含 PE
- 隐含 PS
- 不同 PE 下达成目标市值所需净利润

## scenario-analysis-skill

输出悲观、中性、乐观三情景：

- 收入预测
- 净利润预测
- PE / PS 估值
- 综合市值
- 对应股价

## peer-comparison-skill

1.0 为占位实现，返回可比公司池结构。1.1 接入公开行情后计算同行中位数。

## research-report-skill

串联核心管线并生成 Markdown 投研报告。
