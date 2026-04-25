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

### 3.1 通过飞书界面安装

如果 Hermes Agent 已经完成飞书接入，可以在飞书里直接对 Hermes Bot 发送：

```text
/skills install zhanglunet/valuation-agent --now
```

安装完成后，在飞书新会话中生效；如果需要当前会话立即生效，可以发送：

```text
/reset
```

然后验证：

```text
@Hermes 亚信科技达到 200 亿港币市值，需要什么样的财务表现和估值倍数支撑？
```

如果当前 Hermes 部署不支持从 GitHub repo 自动识别多个 Skill 目录，可以在飞书里让 Hermes 执行以下安装动作：

```text
请安装 valuation-agent：git clone https://github.com/zhanglunet/valuation-agent.git /tmp/valuation-agent，然后把 /tmp/valuation-agent/skills/* 复制到 ~/.hermes/skills/，最后 /reset 让技能生效。
```

### 3.2 通过本地目录导入

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
