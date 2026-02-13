"""校正モードの実装

このモジュールは、異なる校正モード（自動、インタラクティブ、Dry-run）を提供します。
"""

from enum import Enum
from typing import Optional, List, Dict
from pathlib import Path
import json
from datetime import datetime

from src.text_proofreader import TextProofreader, ProofreadingResult


class ProofreadMode(Enum):
    """校正モード"""
    AUTO = "auto"  # 自動修正（確認なし）
    INTERACTIVE = "interactive"  # インタラクティブ（修正案を表示して確認）
    DRY_RUN = "dry-run"  # Dry-run（修正案のみ表示）


class ProofreadHistory:
    """修正履歴を管理するクラス"""
    
    def __init__(self, history_file: Optional[str] = None):
        """
        Args:
            history_file: 履歴ファイルのパス
        """
        self.history_file = history_file or ".proofread_history.json"
        self.history: List[Dict] = []
        self._load_history()
    
    def add_entry(
        self,
        file_path: str,
        mode: ProofreadMode,
        result: ProofreadingResult
    ) -> None:
        """履歴エントリを追加
        
        Args:
            file_path: 処理したファイルのパス
            mode: 使用した校正モード
            result: 校正結果
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "file_path": file_path,
            "mode": mode.value,
            "issues_found": result.issues_found,
            "corrections_applied": result.corrections_applied,
            "has_changes": result.has_changes()
        }
        
        self.history.append(entry)
        self._save_history()
    
    def get_history(self, file_path: Optional[str] = None) -> List[Dict]:
        """履歴を取得
        
        Args:
            file_path: 特定のファイルの履歴のみ取得する場合
        
        Returns:
            履歴エントリのリスト
        """
        if file_path:
            return [e for e in self.history if e['file_path'] == file_path]
        return self.history
    
    def clear_history(self) -> None:
        """履歴をクリア"""
        self.history = []
        self._save_history()
    
    def _load_history(self) -> None:
        """履歴ファイルから読み込み"""
        try:
            path = Path(self.history_file)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
        except Exception:
            self.history = []
    
    def _save_history(self) -> None:
        """履歴ファイルに保存"""
        try:
            path = Path(self.history_file)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception:
            pass


class ProofreadModeHandler:
    """校正モードを処理するハンドラー"""
    
    def __init__(
        self,
        proofreader: TextProofreader,
        history: Optional[ProofreadHistory] = None
    ):
        """
        Args:
            proofreader: TextProofreaderインスタンス
            history: ProofreadHistoryインスタンス
        """
        self.proofreader = proofreader
        self.history = history or ProofreadHistory()
    
    def process(
        self,
        text: str,
        mode: ProofreadMode,
        file_path: Optional[str] = None,
        focus_areas: Optional[List[str]] = None
    ) -> ProofreadingResult:
        """テキストを指定されたモードで処理
        
        Args:
            text: 処理対象のテキスト
            mode: 校正モード
            file_path: ファイルパス（履歴記録用）
            focus_areas: 重点チェック領域
        
        Returns:
            ProofreadingResult: 校正結果
        """
        # 校正を実行
        result = self.proofreader.proofread(text, focus_areas=focus_areas)
        
        # モードに応じた処理
        if mode == ProofreadMode.AUTO:
            # 自動モード: そのまま適用
            final_result = result
        
        elif mode == ProofreadMode.INTERACTIVE:
            # インタラクティブモード: ユーザーに確認
            final_result = self._interactive_mode(result)
        
        elif mode == ProofreadMode.DRY_RUN:
            # Dry-runモード: 修正案のみ表示、適用しない
            final_result = self._dry_run_mode(result)
        
        else:
            final_result = result
        
        # 履歴に記録
        if file_path:
            self.history.add_entry(file_path, mode, final_result)
        
        return final_result
    
    def _interactive_mode(self, result: ProofreadingResult) -> ProofreadingResult:
        """インタラクティブモードの処理
        
        各修正案をユーザーに表示し、適用するか確認します。
        
        Args:
            result: 校正結果
        
        Returns:
            ユーザーの選択を反映した校正結果
        """
        if not result.has_changes():
            print("修正案はありません。")
            return result
        
        print(f"\n{result.issues_found}個の修正案が見つかりました。")
        print("各修正案を確認してください。\n")
        
        # ユーザーの選択を記録
        accepted_changes = []
        rejected_changes = []
        
        for idx, change in enumerate(result.changes, 1):
            print(f"--- 修正案 {idx}/{len(result.changes)} ---")
            print(f"種類: {change.get('type', 'unknown')}")
            print(f"修正前: {change.get('original', '')[:100]}")
            print(f"修正後: {change.get('corrected', '')[:100]}")
            print(f"理由: {change.get('reason', '')}")
            
            # ユーザーに確認
            while True:
                response = input("\nこの修正を適用しますか? (y/n/q): ").lower()
                if response in ['y', 'n', 'q']:
                    break
                print("y (適用), n (スキップ), q (終了) のいずれかを入力してください。")
            
            if response == 'q':
                print("確認を中断しました。")
                break
            elif response == 'y':
                accepted_changes.append(change)
                print("✓ 適用")
            else:
                rejected_changes.append(change)
                print("✗ スキップ")
            
            print()
        
        # 受け入れられた変更のみを適用
        if accepted_changes:
            # 元のテキストに受け入れられた変更を適用
            corrected_text = result.original_text
            for change in accepted_changes:
                original = change.get('original', '')
                corrected = change.get('corrected', '')
                if original and corrected:
                    corrected_text = corrected_text.replace(original, corrected, 1)
            
            # 新しい結果を作成
            from src.text_proofreader import ProofreadingResult
            return ProofreadingResult(
                original_text=result.original_text,
                corrected_text=corrected_text,
                changes=accepted_changes,
                issues_found=result.issues_found,
                corrections_applied=len(accepted_changes),
                diff=self.proofreader._generate_diff(result.original_text, corrected_text)
            )
        else:
            # 変更なし
            from src.text_proofreader import ProofreadingResult
            return ProofreadingResult(
                original_text=result.original_text,
                corrected_text=result.original_text,
                changes=[],
                issues_found=result.issues_found,
                corrections_applied=0,
                diff=""
            )
    
    def _dry_run_mode(self, result: ProofreadingResult) -> ProofreadingResult:
        """Dry-runモードの処理
        
        修正案を表示するだけで、実際には適用しません。
        
        Args:
            result: 校正結果
        
        Returns:
            元のテキストを保持した結果
        """
        print("\n=== Dry-run モード: 修正案のみ表示 ===\n")
        
        if not result.has_changes():
            print("修正案はありません。")
        else:
            print(f"{result.issues_found}個の修正案が見つかりました:\n")
            
            for idx, change in enumerate(result.changes, 1):
                print(f"--- 修正案 {idx} ---")
                print(f"種類: {change.get('type', 'unknown')}")
                print(f"修正前: {change.get('original', '')[:100]}")
                print(f"修正後: {change.get('corrected', '')[:100]}")
                print(f"理由: {change.get('reason', '')}")
                print()
            
            print("\n=== 差分 ===")
            print(result.diff)
        
        # 元のテキストを返す（変更を適用しない）
        from src.text_proofreader import ProofreadingResult
        return ProofreadingResult(
            original_text=result.original_text,
            corrected_text=result.original_text,  # 元のテキストを保持
            changes=result.changes,
            issues_found=result.issues_found,
            corrections_applied=0,  # 適用数は0
            diff=result.diff
        )
    
    def get_history_summary(self) -> str:
        """履歴のサマリーを取得
        
        Returns:
            履歴サマリーの文字列
        """
        history = self.history.get_history()
        
        if not history:
            return "履歴はありません。"
        
        total_files = len(set(e['file_path'] for e in history))
        total_issues = sum(e['issues_found'] for e in history)
        total_corrections = sum(e['corrections_applied'] for e in history)
        
        summary = f"""
校正履歴サマリー:
- 処理ファイル数: {total_files}
- 検出された問題: {total_issues}
- 適用された修正: {total_corrections}
- 最終処理日時: {history[-1]['timestamp']}
"""
        return summary
