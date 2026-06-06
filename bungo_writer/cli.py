import sys
import os
import argparse
import time
import random
from dotenv import load_dotenv

# readlineモジュールをインポートすることで、input()時にバックスペースや矢印キーが正常に機能するようになります
try:
    import readline
except ImportError:
    pass
from bungo_writer.agent import AgentSession

def main():
    # .envファイルから環境変数を読み込む
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="bungo-writer: AIエージェントが文豪として対話するCLIツール")
    parser.add_argument("--author", type=str, default="夏目漱石", help="回答の文体を指定する文豪名 (デフォルト: 夏目漱石)")
    parser.add_argument("--work", type=str, default=None, help="文体を指定する際の具体的な作品名 (例: 吾輩は猫である)")
    parser.add_argument("--review", type=str, default=None, help="指定したファイルやディレクトリを文学作品として批評する")
    parser.add_argument("--provider", type=str, choices=["openai", "gemini"], default="openai", help="使用するLLMプロバイダー (デフォルト: openai)")
    parser.add_argument("--model", type=str, default=None, help="使用するモデル名 (デフォルトはプロバイダーによる)")
    
    args = parser.parse_args()
    
    # 標準入力からのパイプ読み込み
    piped_data = None
    if not sys.stdin.isatty():
        piped_data = sys.stdin.read()
        # パイプから読み込んだ後、対話入力を受け付けるために標準入力をTTYに戻す
        try:
            sys.stdin = open('/dev/tty')
        except OSError:
            pass # TTYが開けない場合はそのまま（Windowsなど）
    
    try:
        print(f"【{args.author} との対話を開始します (終了するには 'exit' または 'quit' を入力)】")
        if piped_data:
            print("※ パイプから初期コンテキストを読み込みました。")
            
        session = AgentSession(
            author=args.author,
            work=args.work,
            review_target=args.review,
            provider=args.provider,
            model=args.model,
            piped_data=piped_data
        )
        
        # レビュー対象が指定されている場合は、初回のアクションを自動実行する
        if args.review:
            initial_instruction = f"対象: {args.review}\n\nこのソースコード（またはディレクトリ）を一つの文学作品として扱い、変数のスコープやライフサイクルを『登場人物の数奇な運命』、バグやスパゲッティコードを『伏線が未回収のまま破綻した悲劇』などに例えて、純文学の批評家のようにレビューしてください。"
            print(f"※ {args.review} の文学的コードレビューを開始します...")
            print("\n", end="")
            for chunk in session.chat(initial_instruction):
                for char in chunk:
                    print(char, end="", flush=True)
                    if char in ["。", "、", "！", "？", "\n"]:
                        time.sleep(random.uniform(0.1, 0.3))
                    else:
                        time.sleep(random.uniform(0.01, 0.04))
            print("\n")
        
        while True:
            try:
                user_input = input("\n> ")
            except EOFError:
                break
            except KeyboardInterrupt:
                break
                
            user_input = user_input.strip()
            if user_input.lower() in ["exit", "quit"]:
                print("対話を終了します。")
                break
            if not user_input:
                continue
            # 以前のDim（淡色）をやめ、通常の明るい文字（エスケープシーケンスなし）で出力します
            print("\n", end="")
            for chunk in session.chat(user_input):
                for char in chunk:
                    print(char, end="", flush=True)
                    
                    # 機械的ではなく、人間が思考しながら書いているような「浮かび上がり」を演出
                    if char in ["。", "、", "！", "？", "\n"]:
                        time.sleep(random.uniform(0.1, 0.3))  # 句読点の後はタメを作る
                    else:
                        time.sleep(random.uniform(0.01, 0.04)) # 通常の文字はランダムな揺らぎで出力
            print("\n") 
            
    except Exception as e:
        print(f"\nエラーが発生しました: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
