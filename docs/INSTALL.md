# 安装与导入

## 1. 安装 Hermes Agent

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
source ~/.zshrc
hermes setup
```

## 2. 配置模型

使用 Hermes 自带命令配置模型供应商：

```bash
hermes model
```

也可以按需设置 OpenRouter Key：

```bash
hermes config set OPENROUTER_API_KEY "your-key"
```

## 3. 导入 Skills

开发期推荐直接在 Hermes 配置中增加本项目路径：

```yaml
skills:
  paths:
    - "~/.hermes/skills"
    - "/Users/john/dev/估值模型/valuation-agent/skills"
```

或者复制：

```bash
mkdir -p ~/.hermes/skills
cp -r /Users/john/dev/估值模型/valuation-agent/skills/* ~/.hermes/skills/
```

## 4. 本地验证

```bash
cd /Users/john/dev/估值模型/valuation-agent
python3 -m unittest discover -s tests
python3 -m valuation_agent.cli generate-report --company asiasoft_1675_hk
```

## 5. Hermes 验收问题

```bash
hermes chat -q "亚信科技达到 200 亿港币市值，需要什么样的财务表现和估值倍数支撑？"
```
