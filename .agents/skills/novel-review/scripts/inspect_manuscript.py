#!/usr/bin/env python3
"""Read-only material inventory and local counts; never a platform approval test."""

import argparse
import hashlib
import json
from pathlib import Path
import re


def inventory(path, role):
    item = {"path": str(path.resolve()), "role": role, "exists": path.is_file()}
    if not item["exists"]:
        item["error"] = "missing_or_not_a_file"
        return item
    try:
        raw = path.read_bytes()
        item["sha256"] = hashlib.sha256(raw).hexdigest()
        text = raw.decode("utf-8-sig")
    except (OSError, UnicodeError) as error:
        item["error"] = str(error)
        return item
    if role == "body":
        if path.suffix.lower() == ".md":
            text = re.sub(r"\A---\r?\n.*?\r?\n---(?:\r?\n|$)", "", text, count=1, flags=re.S)
            text = "\n".join(line for line in text.splitlines()
                             if not re.match(r"^ {0,3}#{1,6}(?:\s|$)", line))
        compact = "".join(text.split())
        item["body_nonwhitespace_chars"] = len(compact)
        item["normalized_body_sha256"] = hashlib.sha256(compact.encode("utf-8")).hexdigest()
        item["empty_body"] = not bool(compact)
    else:
        item["empty_file"] = not bool(text.strip())
    return item


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("本地参考门槛必须大于零")
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", type=Path, action="append", default=[], help="正文文件，可重复")
    parser.add_argument("--outline", type=Path)
    parser.add_argument("--application", type=Path)
    parser.add_argument("--minimum-body-chars", type=positive_int,
                        help="仅在目标通道要求已核实时指定；不是默认平台门槛")
    args = parser.parse_args()
    materials = []
    seen_paths = {}
    seen_bodies = {}
    total = 0
    for path in args.text:
        item = inventory(path, "body")
        resolved = item["path"]
        if resolved in seen_paths:
            item["duplicate_of"] = seen_paths[resolved]
        elif "normalized_body_sha256" in item and not item["empty_body"]:
            body_hash = item["normalized_body_sha256"]
            if body_hash in seen_bodies:
                item["duplicate_of"] = seen_bodies[body_hash]
            else:
                seen_bodies[body_hash] = resolved
                total += item["body_nonwhitespace_chars"]
        seen_paths[resolved] = resolved
        materials.append(item)
    for role in ["outline", "application"]:
        path = getattr(args, role)
        if path is not None:
            materials.append(inventory(path, role))
    count_complete = bool(args.text) and all("error" not in item for item in materials if item["role"] == "body")
    reference = None
    if args.minimum_body_chars is not None:
        reference = {"minimum_body_chars": args.minimum_body_chars,
                     "comparison": ("incomplete_body_inventory" if not count_complete else
                                    "below_local_reference" if total < args.minimum_body_chars else
                                    "at_or_above_local_reference")}
    report = {
        "materials": materials,
        "local_count_basis": "UTF-8正文的非空白字符（含标点和拉丁字符）；Markdown排除frontmatter与标题行；相同路径或规范化正文不重复计数",
        "local_body_chars": total,
        "body_inventory_complete": count_complete,
        "reference_comparison": reference,
        "limitations": ["不等于平台后台字数", "需人工排除空模板、注释和非正文材料", "同章不同版本需人工选定，不可相加", "不判断原创、许可或平台通过"],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
