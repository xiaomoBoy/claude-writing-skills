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
    if len(sys.argv) < 2:
        print("Usage: python3 run_single_score.py <article_path>")
        return 1

    article_path = sys.argv[1]
    prompt_file = REFERENCES_DIR / "score_prompt.md"

    if not prompt_file.exists():
        print(f"Error: {prompt_file} not found")
        return 1

    if not os.path.exists(article_path):
        print(f"Error: {article_path} not found")
        return 1

    scoring_prompt = prompt_file.read_text(encoding="utf-8")
    article_content = Path(article_path).read_text(encoding="utf-8")

    full_prompt = (
        f"{scoring_prompt}\n\n---\n\n## 待评分的文章\n\n{article_content}\n\n---\n\n"
        "请严格按照上述评分维度和JSON格式输出评分结果。只输出JSON，不要输出其他内容。"
    )

    response = get_codex_response(full_prompt)
    score_data = extract_json(response)

    if not score_data:
        print(f"Error: Failed to parse response\n{response}")
        return 1

    dimensions = [
        'title_score', 'opening_score', 'emotion_score', 'info_score',
        'interaction_score', 'structure_score', 'trending_score', 'ip_score'
    ]
    all_dims = dimensions + ['ai_flavor_score']
    actual_total = sum(score_data.get(d, 0) for d in all_dims)
    score_data['total_score'] = actual_total
    score_data['viral_percentage'] = round((actual_total / 90) * 100, 2)

    print(json.dumps(score_data, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
