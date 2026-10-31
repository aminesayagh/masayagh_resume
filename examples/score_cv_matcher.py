#!/usr/bin/env python3
"""Run cv-matcher with a local model and reject its rule-based fallback."""

import argparse
import importlib.metadata
import json
import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("HF_HOME", str(ROOT / ".hf-cache"))
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

from cv_matcher import CVMatcher  # noqa: E402
from cv_matcher.local_analyzer import LocalAIAnalyzer  # noqa: E402
from cv_matcher.models import CVAnalysis, FormattingAdvice, MatchScore  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402
import torch  # noqa: E402


class ModelOnlyAnalyzer(LocalAIAnalyzer):
    """Use cv-matcher's local model and schema without a silent fallback score."""

    def _ensure_model_loaded(self):
        if self.model is not None:
            return
        print(f"Loading model {self.model_name} on {self.device} with SDPA attention...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto" if self.device == "cuda" else None,
            attn_implementation="sdpa",
        )
        if self.device == "cpu":
            self.model = self.model.to("cpu")
        print("Model loaded")

    def _create_analysis_prompt(self, cv_text: str, job_description: str) -> str:
        instructions = (
            "Compare the resume to the job posting using only stated evidence. "
            "Rate four categories separately from 0 to 100: technical skills, "
            "relevant experience, education, and job keywords. "
            "Respond with exactly four whole numbers separated by commas in that "
            "order. No labels, explanation, brackets, or extra text."
        )
        user_message = (
            f"FICTIONAL JOB POSTING:\n{job_description}\n\n"
            f"RESUME TEXT:\n{cv_text}\n\nReturn the four numbers now."
        )
        return self.tokenizer.apply_chat_template(
            [{"role": "system", "content": instructions},
             {"role": "user", "content": user_message}],
            tokenize=False,
            add_generation_prompt=True,
        )

    def analyze(self, cv_text: str, job_description: str):
        self._ensure_model_loaded()
        prompt = self._create_analysis_prompt(cv_text, job_description)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        output = self.model.generate(
            **inputs,
            do_sample=False,
            use_cache=True,
            max_new_tokens=30,
            pad_token_id=self.tokenizer.eos_token_id,
            repetition_penalty=1.1,
        )
        response = self.tokenizer.decode(
            output[0][inputs.input_ids.shape[1]:], skip_special_tokens=True
        )
        debug_file = ROOT / ".hf-cache" / "last_model_response.txt"
        debug_file.parent.mkdir(parents=True, exist_ok=True)
        debug_file.write_text(response, encoding="utf-8")
        match = re.fullmatch(r"\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*", response)
        if match is None:
            raise RuntimeError(f"Local model did not return four scores ({response[:100]!r}); no score was recorded")
        try:
            scores = dict(zip(("skills", "experience", "education", "keywords"), map(float, match.groups())))
            if any(not 0 <= score <= 100 for score in scores.values()):
                raise ValueError("Score outside 0–100")
            matching = [s for s in self.skill_terms if s.lower() in cv_text.lower() and s.lower() in job_description.lower()]
            missing = [s for s in self.skill_terms if s.lower() in job_description.lower() and s.lower() not in cv_text.lower()]
            overall = round(
                0.35 * scores["skills"] + 0.30 * scores["experience"]
                + 0.20 * scores["education"] + 0.15 * scores["keywords"], 1
            )
            summary = (
                "The PDF explicitly mentions " + (", ".join(matching) or "no selected skills") + ". "
                + ("The fictional posting also asks for " + ", ".join(missing)
                   + ", which the PDF does not explicitly mention."
                   if missing else "No selected missing requirements were found.")
            )
            return CVAnalysis(
                match_score=MatchScore(
                    overall_score=overall,
                    skills_match=scores["skills"],
                    experience_match=scores["experience"],
                    education_match=scores["education"],
                    keywords_match=scores["keywords"],
                    matching_skills=matching,
                    missing_skills=missing,
                    matching_keywords=matching,
                    missing_keywords=missing,
                ),
                formatting_advice=FormattingAdvice(
                    strengths=[f"Resume mentions {item}." for item in matching],
                    weaknesses=[f"No clear resume mention of {item}." for item in missing],
                    suggestions=[f"If accurate, add concrete evidence of {item}." for item in missing],
                    structure_feedback="The PDF text is extractable by cv-matcher.",
                    content_feedback=summary,
                ),
                summary=summary,
                recommendation="Tailor the resume with truthful evidence for the missing requirements.",
            )
        except (ValueError, KeyError, TypeError) as error:
            raise RuntimeError("Local model returned invalid scores; no fallback score was recorded") from error


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cv", type=Path, default=ROOT / "output" / "default.pdf")
    parser.add_argument("--job", type=Path, default=ROOT / "examples" / "fictional_full_stack_job.txt")
    parser.add_argument("--out", type=Path, default=ROOT / "analysis" / "fictional_full_stack.json")
    parser.add_argument("--model", default="Qwen/Qwen2.5-1.5B-Instruct")
    parser.add_argument(
        "--skills",
        default="React,Next.js,Python,FastAPI,SQL,PostgreSQL,Docker,CI/CD,AWS,Kubernetes,TypeScript",
        help="Comma-separated skill terms to check literally against the job and PDF",
    )
    args = parser.parse_args()

    cv_path = args.cv.resolve(strict=True)
    job_text = args.job.read_text(encoding="utf-8")
    matcher = CVMatcher(use_local_model=True, local_model_name=args.model)
    matcher.ai_analyzer = ModelOnlyAnalyzer(model_name=args.model)
    matcher.ai_analyzer.skill_terms = [item.strip() for item in args.skills.split(",") if item.strip()]
    analysis = matcher.analyze_cv(str(cv_path), job_text, verbose=True)

    result = {
        "library": "cv-matcher",
        "library_version": importlib.metadata.version("cv-matcher"),
        "model": args.model,
        "backend": "local_model",
        "score_source": "model_category_scores_weighted_by_example_runner",
        "skill_lists_source": "literal_term_presence_in_pdf_and_job_description",
        "fallback_used": False,
        "fictional_job": True,
        "score_is_actual_ats_result": False,
        "cv": os.path.relpath(cv_path, ROOT),
        "job": os.path.relpath(args.job.resolve(), ROOT),
        "analysis": analysis.model_dump(),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    matcher.print_analysis(analysis)
    print(f"Saved {args.out}")


if __name__ == "__main__":
    main()
