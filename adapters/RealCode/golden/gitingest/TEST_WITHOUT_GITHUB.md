# 在没有GitHub账号的情况下测试GitIngest

## 问题背景

原始的测试用例使用了GitHub仓库URL（如 `https://github.com/octocat/Hello-World`），这需要：
1. 网络连接访问GitHub
2. 对于私有仓库测试，需要GitHub账号和访问令牌
3. 可能受到GitHub API速率限制

## 解决方案

我们已经修改了所有测试用例，使用本地Git仓库和文件系统路径代替GitHub URL，这样可以在完全离线环境下运行测试。

## 修改的测试用例

### 1. Feature 1: Repository Cloning
- **原URL**: `https://github.com/octocat/Hello-World`
- **新URL**: `file:///tmp/test-local-repo` (本地Git仓库)
- **原私有仓库**: `https://github.com/user/private-repo`
- **新测试**: `file:///tmp/nonexistent-repo` (模拟克隆失败)

### 2. Feature 4: Web API Interface
- **原输入**: GitHub URL
- **新输入**: 本地路径 (`/tmp/test-local-repo` 或 `/tmp/nonexistent-repo`)

### 3. Feature 5: Command Line Interface
- **原命令**: `gitingest https://github.com/octocat/Hello-World`
- **新命令**: `gitingest /tmp/test-local-repo`

## 如何运行测试

### 方法1: 使用完整的测试套件
```bash
cd /Users/pengzhongyuan/PythonCode/realcode_bench/workspaces/test_gitingest
bash tests/test.sh
```

### 方法2: 使用简化测试脚本
```bash
cd /Users/pengzhongyuan/PythonCode/realcode_bench/workspaces/test_gitingest
bash tests/test_simple.sh
```

### 方法3: 手动设置环境并运行单个测试
```bash
# 1. 设置测试环境
bash tests/setup_test_env.sh

# 2. 运行单个功能测试
python3 gitingest/feature1_clone.py <<< '{"url": "file:///tmp/test-local-repo", "local_path": "/tmp/test-repo", "branch": "main"}'

# 3. 运行文件扫描测试
python3 gitingest/feature2_scan.py <<< '{"local_path": "/tmp/test-project", "ignore_patterns": ["*.pyc", "__pycache__/"]}'
```

## 测试环境详情

运行 `tests/setup_test_env.sh` 会创建以下测试资源：

### 1. 本地Git仓库 (`/tmp/test-local-repo`)
- 包含多种文件类型：Python、JavaScript、Markdown、JSON
- 具有完整的Git历史记录
- 可用于测试克隆、稀疏检出等功能

### 2. 测试项目目录 (`/tmp/test-project`)
- 包含各种文件用于文件扫描测试
- 有Python源文件、编译文件、文本文件等
- 可用于测试文件过滤、大小限制等功能

### 3. 不存在的仓库 (`/tmp/nonexistent-repo`)
- 用于测试错误处理场景
- 模拟克隆失败的情况

## 验证测试是否正常工作

运行以下命令验证测试环境：

```bash
# 验证本地仓库存在且可克隆
python3 gitingest/feature1_clone.py <<< '{"url": "file:///tmp/test-local-repo", "local_path": "/tmp/verify-clone"}'

# 验证文件扫描工作
python3 gitingest/feature2_scan.py <<< '{"local_path": "/tmp/test-project", "max_file_size": 1000}'
```

## 优势

1. **无需网络连接**: 所有测试在本地运行
2. **无需GitHub账号**: 不需要任何GitHub凭证
3. **快速执行**: 没有网络延迟
4. **可重复性**: 每次测试环境一致
5. **无速率限制**: 不受GitHub API限制

## 注意事项

1. 测试会在 `/tmp` 目录创建临时文件，测试结束后会自动清理
2. 如果测试失败，可以手动清理 `/tmp/test-*` 目录
3. 所有测试用例的预期输出已相应调整，以匹配本地仓库的内容

## 恢复原始测试用例

如果需要恢复使用GitHub URL的原始测试用例，可以：

1. 从版本控制恢复原始JSON文件
2. 或者手动将URL改回GitHub地址
3. 注意：恢复后需要GitHub访问权限才能运行测试