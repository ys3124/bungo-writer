import os
import subprocess
from langchain_core.tools import tool

@tool
def list_directory_tool(path: str) -> str:
    """指定したディレクトリの中身（ファイルとサブディレクトリの一覧）を返します。
    引数 path には探索したいディレクトリのパスを指定してください。"""
    try:
        entries = os.listdir(path)
        if not entries:
            return f"ディレクトリ '{path}' は空です。"
        return f"ディレクトリ '{path}' の内容:\n" + "\n".join(entries)
    except Exception as e:
        return f"ディレクトリ '{path}' の読み込みに失敗しました: {e}"

@tool
def read_file_tool(file_path: str) -> str:
    """特定のファイルの中身（ソースコードやテキスト）を読み取って返します。
    引数 file_path には読みたいファイルのパスを指定してください。"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return f"ファイル '{file_path}' の内容:\n\n{content}"
    except Exception as e:
        return f"エラー: ファイル '{file_path}' の読み込みに失敗しました。{str(e)}"

@tool
def git_history_tool(target_path: str = None, n_commits: int = 5) -> str:
    """Gitのコミット履歴を取得します。
    引数 target_path に特定のファイルやディレクトリのパスを指定すると、その対象の履歴のみを取得します。
    引数 n_commits には取得したいコミットの最大件数を指定します（デフォルトは5件）。"""
    try:
        cmd = ["git", "log", "-n", str(n_commits)]
        if target_path:
            cmd.extend(["--", target_path])
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if not result.stdout.strip():
            return "指定された対象のコミット履歴が見つかりませんでした。"
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Gitコマンドの実行に失敗しました。Gitリポジトリではないか、パスが間違っています: {e.stderr}"
    except FileNotFoundError:
        return "エラー: gitコマンドが見つかりません。"
