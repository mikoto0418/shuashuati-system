"""
规则提取题目工具
"""
from dataclasses import dataclass, field
from typing import Dict, List
import re


QUESTION_START_PATTERN = re.compile(r"^\s*(\d+)[\.\、\)]\s*(.+)")
OPTION_PATTERN = re.compile(r"^\s*([A-H])[\.．、\)]\s*(.+)")
ANSWER_PATTERN = re.compile(r"答案[:：]\s*(.+)")
EXPLANATION_PATTERN = re.compile(r"(解析|说明)[:：]\s*(.+)")


@dataclass
class ParsedOption:
    key: str
    content: str


@dataclass
class ParsedQuestion:
    index: int
    question: str
    question_type: str = "single_choice"
    options: List[ParsedOption] = field(default_factory=list)
    answer: str = ""
    explanation: str = ""
    raw_text: str = ""


def _split_question_blocks(text: str) -> List[List[str]]:
    blocks: List[List[str]] = []
    current: List[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if QUESTION_START_PATTERN.match(stripped):
            if current:
                blocks.append(current)
            current = [stripped]
        else:
            if current:
                current.append(stripped)
    if current:
        blocks.append(current)
    return blocks


def _parse_block(lines: List[str]) -> ParsedQuestion:
    first_line = lines[0]
    match = QUESTION_START_PATTERN.match(first_line)
    if not match:
        raise ValueError("题目格式不符合要求")

    index = int(match.group(1))
    body = match.group(2)

    options: List[ParsedOption] = []
    answer = ""
    explanation = ""
    question_lines = [body]

    for line in lines[1:]:
        option_match = OPTION_PATTERN.match(line)
        if option_match:
            options.append(ParsedOption(option_match.group(1), option_match.group(2)))
            continue

        answer_match = ANSWER_PATTERN.search(line)
        if answer_match:
            answer = answer_match.group(1).strip()
            continue

        explanation_match = EXPLANATION_PATTERN.search(line)
        if explanation_match:
            explanation = explanation_match.group(2).strip()
            continue

        question_lines.append(line)

    question_type = "single_choice" if options else "short_answer"

    return ParsedQuestion(
        index=index,
        question="\n".join(question_lines).strip(),
        question_type=question_type,
        options=options,
        answer=answer,
        explanation=explanation,
        raw_text="\n".join(lines),
    )


def parse_questions(text: str) -> List[ParsedQuestion]:
    """
    根据规则解析文本成题目列表。
    """
    blocks = _split_question_blocks(text)
    parsed: List[ParsedQuestion] = []
    for block in blocks:
        try:
            parsed.append(_parse_block(block))
        except ValueError:
            continue
    return parsed
