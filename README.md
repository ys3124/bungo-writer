# 🖋️ bungo-writer (Agent Edition)

無味乾燥なコードやエラーログを文学作品に翻訳するCLIツール「bungo-writer」を、**自律型AIエージェント**としてゼロから構築するためのチュートリアル・リポジトリです。

本リポジトリでは、単なるテキスト変換にとどまらず、AI自身が「ファイルシステムを探索」し、「Webを検索」してコンテキストをかき集め、最終的に一つの文学的なレポートを書き上げるまでのステップを実装します。

## 🎯 アーキテクチャの進化

* **Before (Chain):** ユーザーがコードを与え、AIが翻訳するだけ。（受動的）
* **After (Agent):** ユーザーが「このディレクトリのバグを見て」と指示すると、AIが自らファイルを探し、エラー原因をググり、その結果を文豪風の紀行文として出力する。（自律的）

---

## 🛠️ Step 1: 環境構築とベースラインの準備

まずはLangChainのエージェント機能と、Web検索用のツールパッケージをインストールします。

```bash
# 必要なライブラリのインストール
pip install langchain langchain-openai tavily-python

# APIキーのセットアップ
export OPENAI_API_KEY="your-openai-api-key"
export TAVILY_API_KEY="your-tavily-api-key" # Web検索用のAPI（無料枠あり）

```

---

## 📂 Step 2: ファイルシステム探索ツールの実装

最初のステップでは、AIエージェントが**自律的にローカルディレクトリを歩き回る**ためのツール（目と手）を与えます。

### 実装する機能 (Tools)

LangChainの `@tool` デコレータを使って、以下のPython関数をAI向けツールとして定義します。

1. `list_directory_tool`: 指定したディレクトリの中身（ファイル一覧）を見るツール
2. `read_file_tool`: 特定のファイルの中身（ソースコード）を読むツール

### エージェントの挙動（イメージ）

ユーザー: `"src/ディレクトリの中にある認証(auth)っぽいコードを読んで、太宰治風にレビューして"`
↓

1. AIが自ら `list_directory_tool("src/")` を実行。
2. `auth.py` と `models.py` を発見。
3. AIが自ら `read_file_tool("src/auth.py")` を実行し、コードを読み込む。
4. **出力:** 「私は `src` という暗い森を歩き、`auth.py` の扉を叩いた。そこには……」

---

## 🌐 Step 3: Web検索ツール（Stack Overflow連携）の実装

次に、AIが未知のエラーに遭遇した際、**現実世界の解決策を自らググる**ためのツールを与えます。

### 実装する機能 (Tools)

LangChainに標準搭載されているWeb検索ツールを組み込みます。

* `TavilySearchResults`: 高速で精度の高いAI向け検索APIツール。

### エージェントの挙動（イメージ）

ユーザー: `"この Segmentation Fault のエラーログを解決して、シェイクスピア風に語って"`
↓

1. AIがエラー内容を解析し、「これは自分の知識だけでは足りない」と判断。
2. AIが自ら `TavilySearchResults` を使い、「Linux Segmentation Fault 原因 Python」でWeb検索を実行。
3. Stack Overflowの解決策（メモリ枯渇など）を発見。
4. **出力:** 「おお、哀れなセグメンテーション・フォールトよ！ スタックオーバーフローの賢者たちはこう囁いている。汝のメモリは既に尽き果てたと……」

---

## 🧠 Step 4: エージェントの統合と実行 (AgentExecutor)

Step 2で作った「ファイル探索」と、Step 3で作った「Web検索」のツールを束ね、LLM（GPT-4o等）の脳みそと接続します。

### 実装のコアロジック (疑似コード)

```python
from langchain.agents import create_tool_calling_agent, AgentExecutor

# 1. ツールのリスト化
tools = [list_directory_tool, read_file_tool, tavily_search_tool]

# 2. 文豪ペルソナを持つプロンプトの定義
prompt = """
あなたは {author} です。
ユーザーからの依頼に対し、利用可能なツールを使って調査を行い、
その過程と結果をすべて {author} の文体で、文学的なエッセイとして出力してください。
"""

# 3. エージェントの構築
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 4. 実行
agent_executor.invoke({
    "input": "現在のディレクトリのバグを探して直して",
    "author": "夏目漱石"
})

```

---

## 🚀 使い方 (Usage)

完成したCLIツールは、以下のように人間への指示と同じ感覚で実行できます。

```bash
# ファイル探索からコードレビューまでを丸投げする
bungo-writer "src/ 配下のコード構造を分析して" --author="夏目漱石"

# 未知のエラーログを渡し、Web検索を含めて解決させる
cat error.log | bungo-writer "このエラーの原因を調べて対策を教えて" --author="太宰治"
```

---

## 🗺️ 今後の展望 (Future Roadmap)

現在の「文学的エージェント」というコンセプトをさらに拡張し、他ツールとの絶対的な差別化を図るため、以下の「尖った機能」の実装を予定しています。

### 1. 文学的コードレビュー（作品批評モード）
単なるバグ探しではなく、ソースコードを「一つの文学作品」として批評させる機能（例：`bungo-writer --review src/`）。
変数のスコープを「登場人物の運命」に例えたり、スパゲッティコードを「伏線が未回収のまま破綻した悲劇」としてレビューします。

### 2. 修羅場（締切直前）モード
文豪ならではの「締切に追われる姿」を再現する機能（例：`--deadline` フラグ）。
出力速度が異常に速くなり、「ああ、もう時間がない！」「編集者がドアを叩いている！」という焦燥感とともに、荒々しいが動くハックを提案してくるようになります。

### 3. 自律的な「文学的散歩（Wandering）」
ユーザーが指示を出さなくても、AIが勝手にリポジトリ内を歩き回り、適当なソースコードを立ち読みする機能（例：`bungo-writer wander`）。
気になったコードに対して「この処理は美しい…」などの手記（コメント）を勝手に生成し、プロジェクト内に残していきます。
