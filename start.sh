#!/bin/bash
name=$1
if [ ! -d "target" ]; then
  mkdir "target"
fi
if [ ! -d "translate_results" ]; then
  mkdir "translate_results"
fi
python -m manga_translator --verbose --mode batch --use-gpu --translator=sakura --target-lang=CHS -i ./target/${name}/ -o ./translate_results/${name}_自翻
