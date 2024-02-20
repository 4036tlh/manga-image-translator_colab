#!/bin/bash
if [ ! -d "target" ]; then
  mkdir "target"
fi
if [ ! -d "translate_results" ]; then
  mkdir "translate_results"
fi

target_dir="./target"
result_dir="./translate_results"

for zip in "$target_dir"/*.zip; do

    zip_name=$(basename -- "$zip")

    folder="${zip_name%.*}"
    echo "处理压缩包: $zip_name"

    unzip -o "$zip" -d "$target_dir/$folder"

    python -m manga_translator --verbose --mode batch  --use-gpu --translator=sakura --target-lang=CHS -i ./target/${folder}/ -o ./target/${folder}_自翻

    result_folder="$target_dir/${folder}_自翻"
    zip -r "$result_dir/${folder}_自翻.zip" "$result_folder"

    rm -rf "$target_dir/$folder"
    rm -rf "$result_folder"

    echo "$folder 处理完成"
done

echo "所有压缩包处理完毕"
