#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REFERENCES_DIR = SKILL_DIR / "references"
ASSETS_DIR = SKILL_DIR / "assets"


def resolve_codex_cmd() -> str:
    configured = os.environ.get("CODEX_CLI_PATH")
    if configured:
        return configured
    return "codex"


def get_codex_response(prompt: str, timeout: int = 300) -> str:
    env = os.environ.copy()
    codex_cmd = resolve_codex_cmd()
    codex_bin = str(Path(codex_cmd).expanduser().resolve().parent) if codex_cmd != "codex" else ""
    if codex_bin and codex_bin not in env.get("PATH", ""):
        env["PATH"] = f"{codex_bin}:{env.get('PATH', '')}"

    with tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8", delete=False) as tmp:
        tmp_path = tmp.name

    cmd = [
        codex_cmd,
        "exec",
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "--color",
        "never",
        "-o",
        tmp_path,
        "-",
    ]

    try:
        result = subprocess.run(
            cmd,
            input=prompt,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if os.path.exists(tmp_path):
            output = Path(tmp_path).read_text(encoding="utf-8")
        else:
            output = ""
        if result.returncode != 0 and not output.strip():
            return f"Error: {result.stderr or result.stdout}"
        return output
    except subprocess.TimeoutExpired as e:
        return (e.stdout or "") if isinstance(e.stdout, str) else ""
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def extract_json(text: str):
    if "```json" in text:
        try:
            content = text.split("```json", 1)[1].split("```", 1)[0].strip()
            return json.loads(content)
        except Exception:
            pass
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        try:
            return json.loads(text[start:end + 1])
        except Exception:
            pass
    return None


def main() -> int:
    articles_dir = ASSETS_DIR / "articles" / "samples"
    prompt_file = REFERENCES_DIR / "score_prompt.md"
    output_file = "scores.json"

    if not prompt_file.exists():
        print(f"Error: {prompt_file} not found")
        return 1

    scoring_prompt = prompt_file.read_text(encoding="utf-8")
    article_files = sorted(list(Path(articles_dir).glob("*.md")))
    results = []

    print(f"🚀 开始评分 {len(article_files)} 篇文章...")

    for i, article_path in enumerate(article_files):
        filename = article_path.name
        print(f"[{i+1}/{len(article_files)}] 📝 正在评分: {filename} ...")
        article_content = article_path.read_text(encoding="utf-8")

        full_prompt = (
            f"{scoring_prompt}\n\n---\n\n## 待评分的文章\n\n文件名: {filename}\n\n{article_content}\n\n---\n\n"
            "请严格按照上述评分维度和JSON格式输出评分结果。只输出JSON，不要输出其他内容。"
        )

        response = get_codex_response(full_prompt)
        if not isinstance(response, str):
            response = str(response) if response is not None else ""

        score_data = extract_json(response)
        if score_data:
            dimensions = [
                'title_score', 'opening_score', 'emotion_score', 'info_score',
                'interaction_score', 'structure_score', 'trending_score', 'ip_score',
                'ai_flavor_score'
            ]
            actual_total = sum(score_data.get(d, 0) for d in dimensions)
            score_data['total_score'] = actual_total
            score_data['viral_percentage'] = round((actual_total / 90) * 100, 2)
            print(f"  ✅ 完成: {filename} (总分: {actual_total})")
            results.append({"file": filename, "scores": score_data})
        else:
            print(f"  ❌ 失败: {filename} - 无法解析 JSON 或无响应")
            safe_response = response[:400] if response else ""
            results.append({"file": filename, "scores": {"error": "extraction failed", "raw": safe_response}})

    Path(output_file).write_text(json.dumps({"results": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n🎉 评分全部完成！结果已保存到: {output_file}")
    print("📊 运行评估: python3 evaluate.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
