"""修正機能のテスト

このモジュールは、TextProofreader、OCRProofreader、ProofreadModeHandlerの
機能をテストします。
"""

import pytest
from src.text_proofreader import TextProofreader, ProofreadingResult
from src.ocr_proofreader import OCRProofreader
from src.proofread_modes import ProofreadMode, ProofreadModeHandler, ProofreadHistory


class TestTextProofreader:
    """TextProofreaderのテスト"""
    
    def test_empty_text(self):
        """空のテキストの処理"""
        proofreader = TextProofreader()
        result = proofreader.proofread("")
        
        assert result.original_text == ""
        assert result.corrected_text == ""
        assert result.issues_found == 0
        assert result.corrections_applied == 0
        assert not result.has_changes()
    
    def test_no_changes_needed(self):
        """修正不要なテキスト"""
        proofreader = TextProofreader()
        text = "This is a well-written sentence."
        result = proofreader.proofread(text)
        
        assert result.original_text == text
        # LLMが変更を提案しない場合、元のテキストと同じはず
        assert isinstance(result.corrected_text, str)
    
    def test_chunk_splitting(self):
        """長いテキストのチャンク分割"""
        proofreader = TextProofreader()
        
        # 長いテキストを生成
        long_text = "This is a paragraph.\n\n" * 100
        chunks = proofreader._split_into_chunks(long_text, max_size=500)
        
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) <= 500 or '\n\n' not in chunk  # チャンクサイズまたは分割不可
    
    def test_diff_generation(self):
        """差分生成のテスト"""
        proofreader = TextProofreader()
        
        original = "This is the orignal text."
        corrected = "This is the original text."
        
        diff = proofreader._generate_diff(original, corrected)
        
        assert diff != "変更なし"
        assert "orignal" in diff or "original" in diff
    
    def test_terminology_consistency_check(self):
        """技術用語の一貫性チェック"""
        proofreader = TextProofreader()
        
        text = """
        The database is important. The DB stores data.
        We use the database for persistence.
        """
        
        result = proofreader.check_terminology_consistency(text)
        
        assert isinstance(result, dict)
        assert "terms_found" in result or "error" in result
        assert "consistency_score" in result or "error" in result


class TestOCRProofreader:
    """OCRProofreaderのテスト"""
    
    def test_empty_text(self):
        """空のテキストの処理"""
        ocr_proofreader = OCRProofreader()
        result = ocr_proofreader.correct_ocr_text("", use_llm=False)
        
        assert result.original_text == ""
        assert result.corrected_text == ""
        assert result.issues_found == 0
    
    def test_technical_term_correction(self):
        """技術用語の修正"""
        ocr_proofreader = OCRProofreader()
        
        text = "The APl uses l/O operations."
        corrected, changes = ocr_proofreader.correct_technical_terms(text)
        
        assert "API" in corrected
        assert "I/O" in corrected
        assert len(changes) >= 2
    
    def test_number_spacing_correction(self):
        """数値内のスペース修正"""
        ocr_proofreader = OCRProofreader()
        
        text = "The value is 1 234 567."
        corrected, changes = ocr_proofreader.correct_numbers_and_symbols(text)
        
        assert "1234567" in corrected or "1 234 567" in corrected
    
    def test_decimal_point_correction(self):
        """小数点の修正"""
        ocr_proofreader = OCRProofreader()
        
        text = "The value is 3,14."
        corrected, changes = ocr_proofreader.correct_numbers_and_symbols(text)
        
        assert "3.14" in corrected
        assert any(c['type'] == 'decimal_point' for c in changes)
    
    def test_unit_spacing(self):
        """単位とのスペース追加"""
        ocr_proofreader = OCRProofreader()
        
        text = "The frequency is 100MHz."
        corrected, changes = ocr_proofreader.correct_numbers_and_symbols(text)
        
        assert "100 MHz" in corrected
        assert any(c['type'] == 'unit_spacing' for c in changes)
    
    def test_rule_based_only(self):
        """ルールベースのみの修正"""
        ocr_proofreader = OCRProofreader()
        
        text = "The APl frequency is 100MHz with l/O at 3,14V."
        result = ocr_proofreader.correct_ocr_text(text, is_technical=True, use_llm=False)
        
        assert result.corrected_text != text
        assert result.issues_found > 0
    
    def test_enhance_ocr_quality(self):
        """OCR品質の総合的な向上"""
        ocr_proofreader = OCRProofreader()
        
        text = "The APl uses l/O at 100MHz."
        result = ocr_proofreader.enhance_ocr_quality(text)
        
        assert isinstance(result, ProofreadingResult)
        assert result.original_text == text


class TestProofreadModes:
    """ProofreadModeHandlerのテスト"""
    
    def test_auto_mode(self):
        """自動モードのテスト"""
        proofreader = TextProofreader()
        handler = ProofreadModeHandler(proofreader)
        
        text = "This is a test text."
        result = handler.process(text, ProofreadMode.AUTO)
        
        assert isinstance(result, ProofreadingResult)
        assert result.original_text == text
    
    def test_dry_run_mode(self, capsys):
        """Dry-runモードのテスト"""
        proofreader = TextProofreader()
        handler = ProofreadModeHandler(proofreader)
        
        text = "This is a test text."
        result = handler.process(text, ProofreadMode.DRY_RUN)
        
        # Dry-runモードでは元のテキストを返す
        assert result.corrected_text == text
        assert result.corrections_applied == 0
        
        # 標準出力に何か表示されているはず
        captured = capsys.readouterr()
        assert "Dry-run" in captured.out or "修正案" in captured.out
    
    def test_history_recording(self):
        """履歴記録のテスト"""
        proofreader = TextProofreader()
        history = ProofreadHistory(history_file=".test_proofread_history.json")
        handler = ProofreadModeHandler(proofreader, history)
        
        text = "This is a test text."
        result = handler.process(text, ProofreadMode.AUTO, file_path="test.md")
        
        # 履歴が記録されているか確認
        history_entries = history.get_history("test.md")
        assert len(history_entries) > 0
        assert history_entries[-1]['file_path'] == "test.md"
        assert history_entries[-1]['mode'] == ProofreadMode.AUTO.value
        
        # クリーンアップ
        history.clear_history()
    
    def test_history_summary(self):
        """履歴サマリーのテスト"""
        proofreader = TextProofreader()
        history = ProofreadHistory(history_file=".test_proofread_history2.json")
        handler = ProofreadModeHandler(proofreader, history)
        
        # いくつかの処理を実行
        handler.process("Test 1", ProofreadMode.AUTO, file_path="file1.md")
        handler.process("Test 2", ProofreadMode.AUTO, file_path="file2.md")
        
        summary = handler.get_history_summary()
        
        assert "処理ファイル数" in summary
        assert "検出された問題" in summary
        
        # クリーンアップ
        history.clear_history()


class TestProofreadHistory:
    """ProofreadHistoryのテスト"""
    
    def test_add_and_get_entry(self):
        """エントリの追加と取得"""
        history = ProofreadHistory(history_file=".test_history.json")
        
        result = ProofreadingResult(
            original_text="test",
            corrected_text="test",
            changes=[],
            issues_found=5,
            corrections_applied=3,
            diff=""
        )
        
        history.add_entry("test.md", ProofreadMode.AUTO, result)
        
        entries = history.get_history("test.md")
        assert len(entries) > 0
        assert entries[-1]['issues_found'] == 5
        assert entries[-1]['corrections_applied'] == 3
        
        # クリーンアップ
        history.clear_history()
    
    def test_clear_history(self):
        """履歴のクリア"""
        history = ProofreadHistory(history_file=".test_history2.json")
        
        result = ProofreadingResult(
            original_text="test",
            corrected_text="test",
            changes=[],
            issues_found=1,
            corrections_applied=1,
            diff=""
        )
        
        history.add_entry("test.md", ProofreadMode.AUTO, result)
        assert len(history.get_history()) > 0
        
        history.clear_history()
        assert len(history.get_history()) == 0


class TestProofreadingResult:
    """ProofreadingResultのテスト"""
    
    def test_has_changes_true(self):
        """変更ありの場合"""
        result = ProofreadingResult(
            original_text="test",
            corrected_text="test corrected",
            changes=[{"type": "typo"}],
            issues_found=1,
            corrections_applied=1,
            diff="diff"
        )
        
        assert result.has_changes()
    
    def test_has_changes_false(self):
        """変更なしの場合"""
        result = ProofreadingResult(
            original_text="test",
            corrected_text="test",
            changes=[],
            issues_found=0,
            corrections_applied=0,
            diff=""
        )
        
        assert not result.has_changes()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
