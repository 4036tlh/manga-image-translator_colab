#!/bin/bash

# 定义target文件夹的路径
target_dir="./target"
result_dir="./translate_results"
# 遍历target目录下的所有.zip文件
for zip in "$target_dir"/*.zip; do
    # 获取文件名（包含路径）
    zip_name=$(basename -- "$zip")
    # 获取不带扩展名的文件名作为文件夹名
    folder="${zip_name%.*}"
    echo "处理压缩包: $zip_name"

    # 解压压缩包到target同名文件夹
    unzip -o "$zip" -d "$target_dir/$folder"

    # 使用相对路径运行start.sh脚本，传入文件夹路径
    python -m manga_translator --verbose --mode batch  --use-gpu --translator=sakura --target-lang=CHS -i ./target/${folder}/ -o ./target/${folder}_自翻

    # 将结果文件夹压缩为<文件夹名_自翻.zip>，注意结果文件夹的路径
    result_folder="$target_dir/${folder}_自翻"
    zip -r "$result_dir/${folder}_自翻.zip" "$result_folder"

    # 可选：如果需要删除原始解压的文件夹和翻译结果文件夹，取消下面两行的注释
    rm -rf "$target_dir/$folder"
    rm -rf "$result_folder"

    echo "$folder 处理完成"
done

echo "所有压缩包处理完毕"
