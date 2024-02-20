#/bin/sh
name=$1
python -m manga_translator --verbose --mode batch  --use-gpu --translator=sakura --target-lang=CHS -i ./target/${name}/ -o ./translate_results/${name}_自翻
