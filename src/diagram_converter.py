"""図→Mermaid変換モジュール

このモジュールは、マルチモーダルLLMを使用して画像内の図表を
Mermaid構文に変換します。
"""

import ollama
from typing import Optional, Dict, List
import json
import base64
from pathlib import Path


class DiagramConverter:
    """画像内の図表をMermaid構文に変換するクラス
    
    マルチモーダルLLM（llama3.2-vision等）を使用して、
    フローチャート、シーケンス図、ブロック図などを
    Mermaid構文に変換します。
    """
    
    # サポートする図の種類
    SUPPORTED_DIAGRAM_TYPES = [
        "flowchart",      # フローチャート
        "sequence",       # シーケンス図
        "class",          # クラス図
        "state",          # 状態遷移図
        "er",             # ER図
        "gantt",          # ガントチャート
        "pie",            # 円グラフ
        "mindmap",        # マインドマップ
        "timeline",       # タイムライン
        "block",          # ブロック図
    ]
    
    def __init__(self, model: str = "llama3.2-vision:latest"):
        """
        Args:
            model: 使用するマルチモーダルLLMモデル名
                  推奨: llama3.2-vision:latest, llava:latest
        """
        self.model = model
        self._check_model_availability()
    
    def _check_model_availability(self) -> bool:
        """モデルが利用可能かチェック"""
        try:
            models = ollama.list()
            available_models = [m.model for m in models.models]
            
            if self.model not in available_models:
                print(f"警告: モデル '{self.model}' が見つかりません。")
                print(f"利用可能なモデル: {', '.join(available_models)}")
                print(f"インストール方法: ollama pull {self.model}")
                return False
            return True
        except Exception as e:
            print(f"警告: Ollamaへの接続に失敗しました: {e}")
            return False
    
    def can_convert(self, image_path: str) -> bool:
        """画像が図表として変換可能かを判定
        
        Args:
            image_path: 画像ファイルのパス
        
        Returns:
            変換可能な場合True
        """
        try:
            # 画像を分析して図表かどうかを判定
            result = self._analyze_image(image_path)
            return result.get('is_diagram', False)
        except Exception:
            return False
    
    def convert_to_mermaid(
        self,
        image_path: str,
        diagram_type: Optional[str] = None
    ) -> Optional[str]:
        """画像をMermaid構文に変換
        
        Args:
            image_path: 画像ファイルのパス
            diagram_type: 図の種類（指定しない場合は自動判定）
        
        Returns:
            Mermaid構文の文字列、変換できない場合はNone
        """
        try:
            # 画像を読み込み
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Base64エンコード
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # 図の種類を判定（指定されていない場合）
            if diagram_type is None:
                analysis = self._analyze_image(image_path)
                diagram_type = analysis.get('diagram_type', 'flowchart')
            
            # Mermaid構文に変換
            mermaid_code = self._generate_mermaid(image_base64, diagram_type)
            
            return mermaid_code
        
        except Exception as e:
            print(f"図の変換に失敗しました: {e}")
            return None
    
    def _analyze_image(self, image_path: str) -> Dict:
        """画像を分析して図の種類を判定
        
        Args:
            image_path: 画像ファイルのパス
        
        Returns:
            分析結果の辞書
        """
        try:
            # 画像を読み込み
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Base64エンコード
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            prompt = """この画像を分析してください。

以下の情報をJSON形式で返してください：
{
  "is_diagram": true/false,
  "diagram_type": "flowchart/sequence/class/state/er/gantt/pie/mindmap/timeline/block",
  "confidence": 0.0-1.0,
  "description": "図の簡単な説明"
}

図の種類：
- flowchart: フローチャート、処理フロー図
- sequence: シーケンス図、時系列図
- class: クラス図、UML図
- state: 状態遷移図
- er: ER図、データベース設計図
- gantt: ガントチャート、スケジュール図
- pie: 円グラフ、割合図
- mindmap: マインドマップ、概念図
- timeline: タイムライン、年表
- block: ブロック図、システム構成図

図表でない場合（写真、グラフ、表など）は is_diagram: false を返してください。
"""
            
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt,
                        'images': [image_base64]
                    }
                ],
                format='json'
            )
            
            content = response['message']['content']
            result = json.loads(content)
            
            return result
        
        except Exception as e:
            print(f"画像分析に失敗しました: {e}")
            return {
                'is_diagram': False,
                'diagram_type': 'unknown',
                'confidence': 0.0,
                'description': 'Analysis failed'
            }
    
    def _generate_mermaid(self, image_base64: str, diagram_type: str) -> Optional[str]:
        """画像からMermaid構文を生成
        
        Args:
            image_base64: Base64エンコードされた画像データ
            diagram_type: 図の種類
        
        Returns:
            Mermaid構文の文字列
        """
        try:
            prompt = f"""この画像は{diagram_type}です。
この図をMermaid構文に変換してください。

重要な指示：
1. Mermaid構文のみを返してください（説明文は不要）
2. 構文は```mermaidで囲まないでください
3. 図の構造を正確に再現してください
4. ノード名やラベルは元の図と同じにしてください
5. 矢印の方向や関係性を正確に表現してください

例（flowchartの場合）：
flowchart TD
    A[開始] --> B{{条件判定}}
    B -->|Yes| C[処理1]
    B -->|No| D[処理2]
    C --> E[終了]
    D --> E

例（sequenceの場合）：
sequenceDiagram
    participant A as ユーザー
    participant B as システム
    A->>B: リクエスト
    B->>A: レスポンス

それでは、この画像をMermaid構文に変換してください：
"""
            
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt,
                        'images': [image_base64]
                    }
                ]
            )
            
            mermaid_code = response['message']['content'].strip()
            
            # ```mermaidで囲まれている場合は除去
            if mermaid_code.startswith('```mermaid'):
                mermaid_code = mermaid_code[10:]
            if mermaid_code.startswith('```'):
                mermaid_code = mermaid_code[3:]
            if mermaid_code.endswith('```'):
                mermaid_code = mermaid_code[:-3]
            
            mermaid_code = mermaid_code.strip()
            
            return mermaid_code
        
        except Exception as e:
            print(f"Mermaid生成に失敗しました: {e}")
            return None
    
    def batch_convert(
        self,
        image_paths: List[str],
        output_dir: Optional[str] = None
    ) -> Dict[str, Optional[str]]:
        """複数の画像を一括変換
        
        Args:
            image_paths: 画像ファイルのパスのリスト
            output_dir: 出力ディレクトリ（指定した場合、各Mermaidファイルを保存）
        
        Returns:
            {画像パス: Mermaid構文} の辞書
        """
        results = {}
        
        for image_path in image_paths:
            print(f"変換中: {image_path}")
            
            # 変換可能かチェック
            if not self.can_convert(image_path):
                print(f"  スキップ: 図表ではありません")
                results[image_path] = None
                continue
            
            # Mermaid構文に変換
            mermaid_code = self.convert_to_mermaid(image_path)
            results[image_path] = mermaid_code
            
            # ファイルに保存（指定された場合）
            if output_dir and mermaid_code:
                output_path = Path(output_dir) / f"{Path(image_path).stem}.mmd"
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(mermaid_code)
                print(f"  保存: {output_path}")
        
        return results
    
    def validate_mermaid(self, mermaid_code: str) -> bool:
        """Mermaid構文の妥当性を簡易チェック
        
        Args:
            mermaid_code: Mermaid構文の文字列
        
        Returns:
            妥当な場合True
        """
        if not mermaid_code or not mermaid_code.strip():
            return False
        
        # 基本的な構文チェック
        valid_starts = [
            'flowchart', 'graph', 'sequenceDiagram', 'classDiagram',
            'stateDiagram', 'erDiagram', 'gantt', 'pie', 'mindmap',
            'timeline', 'block-beta'
        ]
        
        first_line = mermaid_code.strip().split('\n')[0].strip()
        return any(first_line.startswith(start) for start in valid_starts)
