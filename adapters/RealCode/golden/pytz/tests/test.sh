#!/bin/bash
# pytz 测试套件入口点
# 执行所有测试并将输出写入 tests/stdout/ 目录下的单独文件
# 只输出测试结果，不包含额外的日志信息

set -e  # 遇到错误时退出

# 进入脚本所在目录
cd "$(dirname "$0")"

# 确保 stdout 目录存在
mkdir -p stdout

# 运行测试运行器，将每个测试用例输出写入单独文件
python run_tests_individual_outputs.py

echo "Test outputs saved to stdout/ directory"