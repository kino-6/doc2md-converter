#!/usr/bin/env python3
"""図→Mermaid変換機能のテストスクリプト

このスクリプトは、DiagramConverterクラスの機能をテストします。
"""

import sys
from pathlib import Path
from src.diagram_converter import DiagramConverter


def test_diagram_conversion():
    """図→Mermaid変換のテスト"""
    
    print("=" * 60)
    print("図→Mermaid変換機能のテスト")
    print("=" * 60)
    print()
    
    # DiagramConverterを初期化
    print("1. DiagramConverterを初期化中...")
    converter = DiagramConverter(model="llama3.2-vision:latest")
    print("   ✓ 初期化完了")
    print()
    
    # テスト用の画像ディレクトリを確認
    test_images_dir = Path("output_test")
    
    # 抽出された画像を検索
    image_dirs = list(test_images_dir.glob("*/images"))
    
    if not image_dirs:
        print("❌ テスト用の画像が見つかりません")
        print(f"   {test_images_dir} 内に画像ディレクトリがありません")
        return
    
    print(f"2. {len(image_dirs)}個の画像ディレクトリを発見")
    print()
    
    # 各ディレクトリから画像を取得
    all_images = []
    for img_dir in image_dirs:
        images = list(img_dir.glob("*.png")) + list(img_dir.glob("*.jpg"))
        all_images.extend(images)
    
    if not all_images:
        print("❌ 画像ファイルが見つかりません")
        return
    
    print(f"3. {len(all_images)}個の画像を発見")
    print()
    
    # 最初の3つの画像をテスト
    test_images = all_images[:min(3, len(all_images))]
    
    print(f"4. {len(test_images)}個の画像をテスト中...")
    print()
    
    for idx, image_path in enumerate(test_images, 1):
        print(f"--- 画像 {idx}/{len(test_images)} ---")
        print(f"ファイル: {image_path.name}")
        print()
        
        # 図かどうかを判定
        print("  ステップ1: 図の判定中...")
        is_diagram = converter.can_convert(str(image_path))
        
        if is_diagram:
            print("  ✓ 図として認識されました")
            print()
            
            # Mermaid構文に変換
            print("  ステップ2: Mermaid構文に変換中...")
            mermaid_code = converter.convert_to_mermaid(str(image_path))
            
            if mermaid_code:
                print("  ✓ 変換成功")
                print()
                print("  生成されたMermaid構文:")
                print("  " + "-" * 50)
                # 最初の10行のみ表示
                lines = mermaid_code.split('\n')[:10]
                for line in lines:
                    print(f"  {line}")
                if len(mermaid_code.split('\n')) > 10:
                    print(f"  ... (残り{len(mermaid_code.split('\n')) - 10}行)")
                print("  " + "-" * 50)
                print()
                
                # Mermaidファイルとして保存
                mermaid_path = image_path.with_suffix('.mmd')
                with open(mermaid_path, 'w', encoding='utf-8') as f:
                    f.write(mermaid_code)
                print(f"  💾 保存: {mermaid_path}")
            else:
                print("  ❌ 変換失敗")
        else:
            print("  ℹ️  図ではありません（スキップ）")
        
        print()
    
    print("=" * 60)
    print("テスト完了")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_diagram_conversion()
    except KeyboardInterrupt:
        print("\n\n中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
