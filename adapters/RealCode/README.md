# 仓库说明
这是 RealCodeBench 相关数据的仓库。下面是各个资源文件夹的说明。

 - `enhanced_test_cases` 包含各个项目的所有测试用例（public & private）。
 - `golden` 包含各个项目的正确实现代码。
 - `test_files` 包含各个项目的 PRD 文档 `start.md`，所有测试用例（public & private）的数量 `test_case_count.txt` 以及测试指令 `test_commands.json`。

## 转换为 Harbor 任务

在 `adapters/RealCode/` 目录下执行：

```bash
python run_adapter.py --output-dir ../../datasets/realcode
```

可选参数：

- `--task-ids`：只转换指定任务（逗号分隔），如 `--task-ids autorccar,pytz`
- `--prefix`：生成任务目录名前缀，默认 `realcode_`




