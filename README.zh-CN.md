# 依赖声明真实性检查器

## 解决的痛点
README 常声称“零依赖”“无需网络”“离线优先”，但锁文件和 import 可能与声明矛盾。

## 为什么现在值得做
AI 生成 README 和快速发布让轻量证据检查对维护者、审查者和安全团队更有价值。

## 安装 / 运行
需要 Python 3.9+，运行时不依赖第三方包。

```bash
python dependency_claim_truth_checker.py --help
```

## 示例
输入：
```text
README: Zero dependencies. requirements.txt: requests==2.0
```

命令：
```bash
python dependency_claim_truth_checker.py examples/demo-project
```

示例输出：
```json
{"claims_found": ["zero_dependencies"], "passed": false}
```

## 自检
```bash
python -m unittest discover -v
```

## 路线图
- 增加更多生态规则。
- 输出 GitHub Actions 注释。
- 支持 SARIF/JSON Lines 以便 CI 使用。

## License
MIT
