#!/usr/bin/env python3
"""
Extractor for large Markdown files guided by MCRD + Truth‑Coder principles.

Inputs:
- Extraction/3.md (source corpus)

Outputs:
- Extraction/3_extraction.json  (rich structured extraction)
- Extraction/3_relations.jsonl  (one triple per line with anchors)
- Extraction/3_distilled.md     (Φ: distilled summary + glyph + metrics)

Approach (deterministic, heuristic):
- Parse markdown structure (headings, lists, code blocks, blockquotes, tables).
- Extract anchors (URLs, numbers, inline code, quotes) for evidence.
- Identify claim sentences from prose (exclude code/quotes/tables) and classify.
- Heuristic triple extraction for simple predicate patterns.
- Detect potential contradictions (negation vs affirmative for same subj/pred).
- Compute Truth‑Coder aligned metrics (approximate): TF, CoI, VI, RR, counts.
- Group by nearest heading to form clusters; compute top entities/terms.
"""

from __future__ import annotations
import json
import os
import re
import sys
import math
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict

SRC_PATH = os.path.join("Extraction", "3.md")
OUT_JSON = os.path.join("Extraction", "3_extraction.json")
OUT_REL = os.path.join("Extraction", "3_relations.jsonl")
OUT_PHI = os.path.join("Extraction", "3_distilled.md")


# ----------------------------
# Utilities
# ----------------------------

STOPWORDS = set(
    """
    a an and are as at be by for from has have i if in into is it its of on or our out that the their there these they this to was were will with you your we not can may should must 
    """.split()
)


def tokenize(text: str) -> list[str]:
    # Basic tokenization: lowercase words, strip punctuation
    tokens = re.findall(r"[A-Za-z0-9_\-]+", text.lower())
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


def is_heading(line: str) -> int:
    m = re.match(r"^(#{1,6})\s+", line)
    return len(m.group(1)) if m else 0


def extract_links(text: str) -> list[tuple[str, str]]:
    # Markdown links [text](url)
    return re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text)


def extract_images(text: str) -> list[tuple[str, str]]:
    return re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", text)


def has_table_line(line: str) -> bool:
    return ("|" in line) and (re.search(r"^\s*\|.*\|\s*$", line) is not None)


def classify_sentence(s: str) -> tuple[str, list[str]]:
    # type, modality tags
    text = s.strip()
    mods = []
    type_ = "other"
    lower = text.lower()

    for kw in ("must", "should", "shall", "require", "required", "needs to"):
        if kw in lower:
            mods.append(kw)
    if text.endswith("?"):
        type_ = "question"
    elif any(kw in lower for kw in ("must", "should", "shall", "require")):
        type_ = "rule"
    elif re.search(r"\b(is|are|means|equals|:=|:|->)\b", text):
        type_ = "definition"
    elif any(kw in lower for kw in ("use ", "create ", "build ", "implement ", "install ", "configure ", "run ", "call ")):
        type_ = "instruction"
    elif any(ch.isdigit() for ch in text):
        type_ = "observation"
    return type_, mods


def extract_triple(text: str) -> dict[str, str] | None:
    # Very simple pattern-based triples
    # Patterns: X is Y; X are Y; X has Y; X uses Y; X -> Y; X: Y
    patterns = [
        (re.compile(r"^(.+?)\s+is\s+(.+)$", re.I), "is"),
        (re.compile(r"^(.+?)\s+are\s+(.+)$", re.I), "are"),
        (re.compile(r"^(.+?)\s+has\s+(.+)$", re.I), "has"),
        (re.compile(r"^(.+?)\s+have\s+(.+)$", re.I), "have"),
        (re.compile(r"^(.+?)\s+uses\s+(.+)$", re.I), "uses"),
        (re.compile(r"^(.+?)\s+supports\s+(.+)$", re.I), "supports"),
        (re.compile(r"^(.+?)\s*->\s*(.+)$", re.I), "maps_to"),
        (re.compile(r"^([^:]{2,}):\s*(.+)$", re.I), "defines"),
    ]
    t = text.strip().strip(".`")
    for rx, pred in patterns:
        m = rx.match(t)
        if m:
            subj = re.sub(r"\s+", " ", m.group(1)).strip()
            obj = re.sub(r"\s+", " ", m.group(2)).strip()
            # Avoid super short or trivial triples
            if len(subj) >= 2 and len(obj) >= 2 and not subj.endswith(":"):
                return {"subj": subj, "pred": pred, "obj": obj}
    return None


def negation_polarity(text: str) -> int:
    # 1 for affirmative, -1 for negated
    return -1 if re.search(r"\bnot\b|\bcannot\b|\bcan't\b|\bno\b|\bnever\b", text.lower()) else 1


def extract_numbers(text: str) -> list[str]:
    return re.findall(r"(?<![A-Za-z])\d[\d,\.]*", text)


def split_sentences(text: str) -> list[str]:
    # Simple sentence splitter—good enough for heuristic claims
    # Keep question marks and exclamation points attached
    parts = re.split(r"(?<=[\.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def sanitize(text: str) -> str:
    return text.replace("\u0000", " ")


# ----------------------------
# Main extraction routine
# ----------------------------

def extract_markdown(path: str) -> dict:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        raw_lines = f.readlines()

    lines = [sanitize(x.rstrip("\n")) for x in raw_lines]

    headings = []
    code_blocks = []
    blockquotes = []
    lists = []
    tables = []
    links = []
    images = []
    inline_codes = []
    claims = []
    relations = []

    in_code = False
    code_lang = ""
    code_start = None
    table_buf = []

    # Track current heading context stack
    context_stack: list[tuple[int, str, int]] = []  # (level, text, line)

    # Map each line to nearest heading path
    line_context = {}

    for i, line in enumerate(lines, start=1):
        # Track line → heading path
        lvl = is_heading(line)
        if lvl:
            text = re.sub(r"^#+\s+", "", line).strip()
            while context_stack and context_stack[-1][0] >= lvl:
                context_stack.pop()
            context_stack.append((lvl, text, i))
            path = " / ".join([h[1] for h in context_stack])
            headings.append({"level": lvl, "text": text, "line": i, "path": f"{SRC_PATH}:{i}"})
            line_context[i] = path
            continue

        # Code blocks
        if line.strip().startswith("```"):
            if not in_code:
                in_code = True
                code_lang = line.strip().strip("`").strip()
                code_start = i
            else:
                in_code = False
                code_blocks.append({
                    "lang": code_lang or "", "start_line": code_start, "end_line": i,
                    "path": f"{SRC_PATH}:{code_start}"
                })
                code_lang = ""
                code_start = None
            continue

        if in_code:
            # Skip parsing other structures while inside code
            continue

        # Blockquotes
        if line.strip().startswith(">"):
            blockquotes.append({"text": line.lstrip("> "), "line": i, "path": f"{SRC_PATH}:{i}"})
            continue

        # Tables (accumulate consecutive table lines)
        if has_table_line(line):
            table_buf.append((i, line))
        else:
            if table_buf:
                start = table_buf[0][0]
                end = table_buf[-1][0]
                tables.append({"start_line": start, "end_line": end, "path": f"{SRC_PATH}:{start}"})
                table_buf = []

        # Lists and tasks
        m_task = re.match(r"^\s*[-*+]\s+\[( |x|X)\]\s+(.*)$", line)
        if m_task:
            checked = m_task.group(1).lower() == "x"
            lists.append({"type": "task", "checked": checked, "text": m_task.group(2).strip(), "line": i, "path": f"{SRC_PATH}:{i}"})
            continue
        m_bullet = re.match(r"^\s*[-*+]\s+(.*)$", line)
        if m_bullet:
            lists.append({"type": "bullet", "text": m_bullet.group(1).strip(), "line": i, "path": f"{SRC_PATH}:{i}"})
            continue
        m_num = re.match(r"^\s*\d+\.[)\s]+(.*)$", line)
        if m_num:
            lists.append({"type": "number", "text": m_num.group(1).strip(), "line": i, "path": f"{SRC_PATH}:{i}"})
            continue

        # Links & images & inline code
        for (txt, url) in extract_links(line):
            links.append({"text": txt, "url": url, "line": i, "path": f"{SRC_PATH}:{i}"})
        for (alt, url) in extract_images(line):
            images.append({"alt": alt, "url": url, "line": i, "path": f"{SRC_PATH}:{i}"})
        for code in re.findall(r"`([^`]+)`", line):
            inline_codes.append({"code": code, "line": i, "path": f"{SRC_PATH}:{i}"})

        # Claim sentences: from plain text lines (ignore blank, headings, code, quotes, lists)
        if line.strip() and not any(line.strip().startswith(x) for x in ("#", ">", "- ", "* ", "+ ", "|")):
            # Split into sentences
            for s in split_sentences(line):
                stype, mods = classify_sentence(s)
                nums = extract_numbers(s)
                lnks = [u for (_, u) in extract_links(s)]
                ev = {"urls": lnks, "numbers": nums, "quotes": '"' in s}
                trip = extract_triple(s)
                claim = {
                    "sentence": s,
                    "line": i,
                    "path": f"{SRC_PATH}:{i}",
                    "type": stype,
                    "modality": mods,
                    "evidence": ev,
                    "triple": trip,
                    "polarity": negation_polarity(s),
                }
                claims.append(claim)
                if trip:
                    relations.append({
                        "subj": trip["subj"],
                        "pred": trip["pred"],
                        "obj": trip["obj"],
                        "line": i,
                        "path": f"{SRC_PATH}:{i}",
                        "polarity": claim["polarity"],
                    })

    # Close any pending table buffer
    if table_buf:
        start = table_buf[0][0]
        end = table_buf[-1][0]
        tables.append({"start_line": start, "end_line": end, "path": f"{SRC_PATH}:{start}"})

    # Build clusters by nearest heading
    def nearest_context(line_no: int) -> str:
        # Find the deepest heading with line <= line_no
        ctx = [h for h in headings if h["line"] <= line_no]
        if not ctx:
            return ""
        ctx.sort(key=lambda h: (h["line"], h["level"]))
        # Build path from all headings before line_no
        stack = []
        for h in headings:
            if h["line"] <= line_no:
                while stack and stack[-1]["level"] >= h["level"]:
                    stack.pop()
                stack.append(h)
        return " / ".join([x["text"] for x in stack])

    clusters = defaultdict(lambda: {"claims": [], "relations": []})
    for idx, c in enumerate(claims):
        ctx = nearest_context(c["line"]) or "(root)"
        clusters[ctx]["claims"].append(idx)
    for idx, r in enumerate(relations):
        ctx = nearest_context(r["line"]) or "(root)"
        clusters[ctx]["relations"].append(idx)

    # Detect contradictions: same subj+pred with opposing polarity
    contradictions = []
    by_pair = defaultdict(list)
    for r in relations:
        key = (r["subj"].lower(), r["pred"].lower())
        by_pair[key].append(r)
    for key, arr in by_pair.items():
        pols = set(a["polarity"] for a in arr)
        if len(pols) > 1:
            # capture minimal pair
            pos = next((a for a in arr if a["polarity"] == 1), None)
            neg = next((a for a in arr if a["polarity"] == -1), None)
            if pos and neg:
                contradictions.append({
                    "subject": pos["subj"],
                    "predicate": pos["pred"],
                    "line_true": pos["line"],
                    "line_false": neg["line"],
                    "path_true": pos["path"],
                    "path_false": neg["path"],
                    "sentence_true": next((c["sentence"] for c in claims if c["line"] == pos["line"]), ""),
                    "sentence_false": next((c["sentence"] for c in claims if c["line"] == neg["line"]), ""),
                })

    # Entities: top tokens from headings + claims
    token_counter = Counter()
    for h in headings:
        token_counter.update(tokenize(h["text"]))
    for c in claims:
        token_counter.update(tokenize(c["sentence"]))
    entities = [{"text": t, "count": n} for t, n in token_counter.most_common(200)]

    # Metrics (Truth‑Coder aligned, approximate)
    total_rel = len(relations)
    contract_like = sum(1 for c in claims if c["type"] == "rule")
    coi = (contract_like / total_rel) if total_rel else 0.0
    tf = (sum(1 for c in claims if c["evidence"]["urls"] or c["evidence"]["numbers"]) / max(1, len(claims)))
    vi = (sum(1 for c in claims if c["evidence"]["urls"]) / max(1, contract_like)) if contract_like else 0.0
    # Resonance ratio: compression (unique clusters) vs expansion (avg items per cluster)
    num_clusters = len(clusters)
    items_per_cluster = sum(len(v["claims"]) + len(v["relations"]) for v in clusters.values()) / max(1, num_clusters)
    compression_index = num_clusters / max(1, len(headings) or 1)
    expansion_index = items_per_cluster / max(1, num_clusters)
    rr = (compression_index / max(1e-9, expansion_index)) if expansion_index else 0.0

    metrics = {
        "counts": {
            "lines": len(lines),
            "headings": len(headings),
            "code_blocks": len(code_blocks),
            "tables": len(tables),
            "lists": len(lists),
            "blockquotes": len(blockquotes),
            "links": len(links),
            "images": len(images),
            "inline_codes": len(inline_codes),
            "claims": len(claims),
            "relations": len(relations),
            "entities": len(entities),
            "contradictions": len(contradictions),
            "clusters": num_clusters,
        },
        "truth_coder": {
            "CoherenceIndex_CoI": round(coi, 3),
            "TraceFidelity_TF": round(tf, 3),
            "ValidationIntegrity_VI": round(vi, 3),
            "ResonanceRatio_RR": round(rr, 3),
        },
    }

    # Prepare cluster list view
    cluster_list = []
    for k, v in clusters.items():
        cluster_list.append({"heading": k, "claims": v["claims"], "relations": v["relations"]})
    cluster_list.sort(key=lambda x: x["heading"])  # alphabetical

    doc = {
        "source": SRC_PATH,
        "headings": headings,
        "code_blocks": code_blocks,
        "tables": tables,
        "lists": lists,
        "blockquotes": blockquotes,
        "links": links,
        "images": images,
        "inline_codes": inline_codes,
        "claims": claims,
        "relations": relations,
        "contradictions": contradictions,
        "entities": entities,
        "clusters": cluster_list,
        "metrics": metrics,
    }
    return doc


def write_outputs(doc: dict):
    # JSON extraction
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False)

    # Relations JSONL
    with open(OUT_REL, "w", encoding="utf-8") as f:
        for r in doc.get("relations", []):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Distilled Φ summary
    m = doc["metrics"]
    top_entities = ", ".join(e["text"] for e in doc["entities"][:12])
    # Glyph: name = top three tokens joined; tagline from high-level stats
    glyph_name = "Γ-" + "-".join(e["text"] for e in doc["entities"][:3]) if doc["entities"] else "Γ-phi"
    tagline = f"Distilled field: {m['counts']['claims']} claims, {m['counts']['relations']} relations, {m['counts']['headings']} headings."
    tc = m["truth_coder"]

    lines = []
    lines.append("# Φ — Distilled Summary (MCRD × Truth‑Coder)")
    lines.append("")
    lines.append("## Glyph")
    lines.append(f"- Name: {glyph_name}")
    lines.append(f"- Tagline: {tagline}")
    lines.append(f"- Top Entities: {top_entities}")
    lines.append("")
    lines.append("## Metrics")
    lines.append(f"- CoI: {tc['CoherenceIndex_CoI']}")
    lines.append(f"- TF: {tc['TraceFidelity_TF']}")
    lines.append(f"- VI: {tc['ValidationIntegrity_VI']}")
    lines.append(f"- RR: {tc['ResonanceRatio_RR']}")
    lines.append("")
    lines.append("## Invariants (Top Relational Patterns)")
    # Show top 10 relations by frequency of (subj,pred,obj)
    rel_counter = Counter((r["subj"], r["pred"], r["obj"]) for r in doc.get("relations", []))
    for (subj, pred, obj), cnt in rel_counter.most_common(10):
        lines.append(f"- {subj} —{pred}→ {obj} (×{cnt})")
    if not rel_counter:
        lines.append("- (No simple triples extracted)")
    lines.append("")
    lines.append("## Paradoxes (Potential Contradictions)")
    if doc.get("contradictions"):
        for c in doc["contradictions"][:10]:
            lines.append(f"- {c['subject']} —{c['predicate']}→ [affirm:{c['path_true']}] vs [neg:{c['path_false']}]")
    else:
        lines.append("- None detected by heuristic scan")
    lines.append("")
    lines.append("## Clusters (by Heading)")
    for cl in doc.get("clusters", [])[:20]:
        lines.append(f"- {cl['heading']}: {len(cl['claims'])} claims, {len(cl['relations'])} relations")

    with open(OUT_PHI, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    if not os.path.exists(SRC_PATH):
        print(f"Source not found: {SRC_PATH}", file=sys.stderr)
        sys.exit(2)
    doc = extract_markdown(SRC_PATH)
    write_outputs(doc)
    # Print brief to stdout for quick check
    m = doc["metrics"]
    print(json.dumps({
        "source": SRC_PATH,
        "counts": m["counts"],
        "truth_coder": m["truth_coder"],
        "outputs": {"json": OUT_JSON, "relations": OUT_REL, "phi": OUT_PHI}
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

