#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
目录树生成器 - S_01_moctree.py

自动生成项目的目录树文档，使用经典 tree 命令风格。
扫描 backend/ 和 research/ 核心目录，完全展开显示所有子目录和关键文件。
"""

import os
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Set


class MoctreeGenerator:
    """目录树生成器"""

    # 需要显示的文件扩展名（关键文件）
    KEY_EXTENSIONS = {
        '.md', '.yaml', '.yml', '.json', '.txt', '.py',
        '.toml', '.ini', '.cfg', '.sh', '.bat'
    }

    # 需要排除的目录名
    EXCLUDE_DIRS = {
        '__pycache__', '.git', '.venv', 'venv', 'env',
        '.pytest_cache', '.idea', '.vscode', '.DS_Store',
        'node_modules', '.tox', '.eggs', '*.egg-info',
        '_reference'  # 排除参考资料库
    }

    # 需要排除的文件名
    EXCLUDE_FILES = {
        '.gitkeep', '.gitignore', '.DS_Store',
        'Thumbs.db', 'desktop.ini'
    }

    # 始终显示的文件名（无论扩展名）
    ALWAYS_SHOW = {
        'README', 'LICENSE', 'Makefile', 'Dockerfile',
        '.gitignore', 'requirements.txt', 'setup.py'
    }

    def __init__(self, root_dir: str = None):
        """
        初始化生成器

        Args:
            root_dir: 项目根目录，默认为脚本所在目录的上级
        """
        if root_dir is None:
            # 默认为脚本所在目录的上级
            self.root_dir = Path(__file__).parent.parent.resolve()
        else:
            self.root_dir = Path(root_dir).resolve()

    def should_show_file(self, filename: str) -> bool:
        """
        判断文件是否应该显示

        Args:
            filename: 文件名

        Returns:
            是否显示
        """
        # 检查是否在排除列表
        if filename in self.EXCLUDE_FILES:
            return False

        # 检查是否在始终显示列表
        if filename in self.ALWAYS_SHOW:
            return True

        # 检查扩展名
        ext = Path(filename).suffix.lower()
        return ext in self.KEY_EXTENSIONS

    def should_show_dir(self, dirname: str) -> bool:
        """
        判断目录是否应该显示

        Args:
            dirname: 目录名

        Returns:
            是否显示
        """
        return dirname not in self.EXCLUDE_DIRS

    def get_tree_lines(
        self,
        directory: Path,
        prefix: str = '',
        is_last: bool = True,
        level: int = 0
    ) -> List[str]:
        """
        递归生成目录树的行列表

        Args:
            directory: 当前目录
            prefix: 当前行前缀
            is_last: 是否是同级最后一项
            level: 当前深度

        Returns:
            树状图的行列表
        """
        lines = []
        max_level = 10  # 最大深度限制

        if level > max_level:
            return lines

        try:
            # 获取所有子项
            entries = list(directory.iterdir())
            if not entries:
                return lines

            # 分离目录和文件
            dirs = []
            files = []

            for entry in entries:
                if entry.name.startswith('.'):
                    # 跳过隐藏文件和目录（除了 .gitignore 等特定文件）
                    if entry.name not in self.ALWAYS_SHOW:
                        continue

                if entry.is_dir():
                    if self.should_show_dir(entry.name):
                        dirs.append(entry)
                elif entry.is_file():
                    if self.should_show_file(entry.name):
                        files.append(entry)

            # 排序：目录和文件分别按字母排序
            dirs.sort(key=lambda x: x.name.lower())
            files.sort(key=lambda x: x.name.lower())

            # 合并：目录在前，文件在后
            all_entries = dirs + files

            # 生成树状图
            for i, entry in enumerate(all_entries):
                is_last_item = (i == len(all_entries) - 1)

                # 确定连接符和子项前缀
                if is_last_item:
                    connector = '└── '
                    child_prefix = prefix + '    '
                else:
                    connector = '├── '
                    child_prefix = prefix + '│   '

                # 添加当前行
                lines.append(f"{prefix}{connector}{entry.name}")

                # 如果是目录，递归处理子项
                if entry.is_dir():
                    sub_lines = self.get_tree_lines(
                        entry,
                        child_prefix,
                        True,  # 子项内部的 is_last 不影响前缀
                        level + 1
                    )
                    lines.extend(sub_lines)

        except PermissionError:
            lines.append(f"{prefix}    [权限受限，无法访问]")
        except Exception as e:
            lines.append(f"{prefix}    [错误: {str(e)}]")

        return lines

    def generate_tree(self, dirs_to_scan: List[str] = None) -> str:
        """
        生成完整的目录树

        Args:
            dirs_to_scan: 要扫描的目录列表（相对于根目录）
                         默认为 ['backend', 'research']

        Returns:
            目录树字符串
        """
        if dirs_to_scan is None:
            dirs_to_scan = ['backend', 'research']

        lines = []

        # 添加标题和时间戳
        title = "研究OS_项目目录树"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        lines.append(f"{title}")
        lines.append(f"生成时间: {timestamp}")
        lines.append("")

        # 对每个目录生成树状图
        for i, dir_name in enumerate(dirs_to_scan):
            dir_path = self.root_dir / dir_name

            if not dir_path.exists():
                lines.append(f"[{dir_name}/] - 目录不存在")
                lines.append("")
                continue

            # 添加目录标题
            lines.append(f"{dir_name}/")
            lines.append("")

            # 生成该目录的树状图
            tree_lines = self.get_tree_lines(dir_path, '', True, 0)

            if tree_lines:
                lines.extend(tree_lines)
            else:
                lines.append("    [空目录]")

            # 目录之间添加空行
            if i < len(dirs_to_scan) - 1:
                lines.append("")

        # 添加统计信息
        lines.append("")
        lines.append("---")
        lines.append(f"根目录: {self.root_dir}")
        lines.append(f"扫描目录: {', '.join(dirs_to_scan)}")

        return '\n'.join(lines)

    def save_to_file(self, content: str, output_path: str = None) -> Path:
        """
        保存目录树到文件

        Args:
            content: 目录树内容
            output_path: 输出文件路径，默认为根目录的 目录树.md

        Returns:
            保存的文件路径
        """
        if output_path is None:
            output_path = self.root_dir / '目录树.md'
        else:
            output_path = Path(output_path).resolve()

        # 确保输出目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return output_path


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='生成项目目录树文档',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python S_01_moctree.py                    # 使用默认设置生成目录树
  python S_01_moctree.py -d backend research  # 指定要扫描的目录
  python S_01_moctree.py -o /path/to/output.md  # 指定输出文件
  python S_01_moctree.py -r /path/to/project  # 指定项目根目录
        """
    )

    parser.add_argument(
        '-d', '--dirs',
        nargs='+',
        default=['backend', 'research'],
        help='要扫描的目录列表（默认: backend research）'
    )

    parser.add_argument(
        '-o', '--output',
        default=None,
        help='输出文件路径（默认: 项目根目录/目录树.md）'
    )

    parser.add_argument(
        '-r', '--root',
        default=None,
        help='项目根目录（默认: 脚本所在目录的上级）'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='只打印结果，不写入文件'
    )

    args = parser.parse_args()

    # 创建生成器
    generator = MoctreeGenerator(root_dir=args.root)

    # 生成目录树
    tree_content = generator.generate_tree(dirs_to_scan=args.dirs)

    # 输出结果
    if args.dry_run:
        print(tree_content)
    else:
        output_path = generator.save_to_file(tree_content, args.output)
        print(f"目录树已生成: {output_path}")
        print(f"扫描目录: {', '.join(args.dirs)}")


if __name__ == '__main__':
    main()
