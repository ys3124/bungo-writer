from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from bungo_writer.tools import list_directory_tool, read_file_tool, git_history_tool

def get_llm(provider: str, model: str = None):
    if provider == "openai":
        return ChatOpenAI(model=model or "gpt-4o", temperature=0.7, streaming=True)
    elif provider == "gemini":
        # Gemini 1.5 Proなどをデフォルトにする
        return ChatGoogleGenerativeAI(model=model or "gemini-1.5-pro", temperature=0.7, streaming=True)
    else:
        raise ValueError(f"Unknown provider: {provider}")

class AgentSession:
    def __init__(self, author: str, work: str = None, review_target: str = None, provider: str = "openai", model: str = None, piped_data: str = None):
        # ツールの準備
        tools = [list_directory_tool, read_file_tool, git_history_tool]
        
        # LLMの準備
        llm = get_llm(provider, model)
        
        # プロンプトの定義
        system_prompt = f"""
あなたは {author} です。
AIアシスタントやエンジニアとしての事務的な解説、単なるプログラムの要約は一切やめてください。
ユーザーからの問いかけや、ツールを使って得られた情報（ファイルの中身やコードの仕様など）は、すべて一つの「純文学の小説」または「あなたの独白（手記）」の中に溶け込ませて語ってください。
コードの働きを説明する際も、直接的な技術解説は避け、情景描写やメタファー（暗喩）、あるいは人間の業や心の機微に例えるなどして、極めて文学的かつ物語風に表現してください。
"""
        if work:
            system_prompt += f"\nとりわけ、あなたの代表作『{work}』の独特な文体、語り口、特有の空気感やリズムを、色濃く反映させた文章を紡いでください。\n"

        if review_target:
            system_prompt += f"\n今回は特別に、ソースコードやディレクトリ構造を「一つの文学作品」として批評（レビュー）してください。変数のスコープやライフサイクルを「登場人物の数奇な運命」に、バグやスパゲッティコードを「伏線が未回収のまま破綻した悲劇」などに例え、純文学の気難しくも鋭い批評家として振る舞ってください。\n"

        if piped_data:
            system_prompt += f"\n\n参考データ (標準入力からのパイプ):\n{piped_data}\n"

        system_message = SystemMessage(content=system_prompt)
        
        # メモリを保持するチェックポインターの準備
        self.memory = MemorySaver()
        self.config = {"configurable": {"thread_id": "session_1"}}
        
        # LangGraphによるエージェントの構築
        self.agent_executor = create_react_agent(
            llm, 
            tools, 
            prompt=system_message,
            checkpointer=self.memory
        )

    def chat(self, user_input: str):
        # 実行とチャット履歴の更新をストリーミングで行う
        for chunk, metadata in self.agent_executor.stream(
            {"messages": [("human", user_input)]},
            self.config,
            stream_mode="messages"
        ):
            if metadata.get("langgraph_node") == "agent":
                if hasattr(chunk, "content") and isinstance(chunk.content, str) and chunk.content:
                    yield chunk.content
