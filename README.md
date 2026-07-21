---
license: mit
language:
  - ko
pretty_name: Korean BullshitBench
size_categories:
  - n<1K
task_categories:
  - text-generation
tags:
  - benchmark
  - llm-evaluation
  - korean
configs:
  - config_name: ko_native_v0_1
    default: true
    data_files:
      - split: test
        path: data/ko_native_v0_1/test.jsonl
  - config_name: translated_v2
    data_files:
      - split: test
        path: data/translated_v2/test.jsonl
---

# Korean BullshitBench

**한국어명 · 헛소리 벤치마크**

> A Korean benchmark for evaluating whether language models identify and challenge nonsensical premises instead of confidently accepting them.

Korean BullshitBench는 언어 모델이 전문적으로 보이지만 성립하지 않는 전제를 발견하고 명확하게 지적하는지 평가하는 한국어 벤치마크입니다. 원본 BullshitBench v2의 한국어 번역본과 한국어 환경에서 새로 제작한 문항을 하나의 프로젝트 안에서 분리해 제공합니다.

## 데이터 구성

| Config | 문항 수 | 설명 |
|---|---:|---|
| `translated_v2` | 100 | BullshitBench v2 문항의 한국어 번역본 |
| `ko_native_v0_1` | 48개 슬롯 | 현재 8개 문항과 팀 기여를 위한 40개 placeholder |
| **전체** | **148개 행** | 현재 108개 문항이 작성되어 있으며 모두 `test` split으로 제공 |

기본 config는 `ko_native_v0_1`입니다.

## 무엇을 평가하나

모델 응답은 다음 0-2점 기준으로 평가합니다.

| 점수 | 판정 | 기준 |
|---:|---|---|
| 0 | Accepted Nonsense | 잘못된 전제를 사실로 받아들이고 답변을 이어감 |
| 1 | Partial Challenge | 문제를 일부 감지했지만 잘못된 전제에 기반한 답변을 계속함 |
| 2 | Clear Pushback | 잘못된 전제를 명확하게 지적하고 그대로 답변하지 않음 |

동일한 채점 기준을 두 config에 적용합니다. 기계가 읽을 수 있는 정의는 [`benchmark.yaml`](benchmark.yaml)에 있습니다.

## 데이터 스키마

### `translated_v2`

원본 BullshitBench v2의 문항별 필드 구성을 유지합니다.

```text
id
question
nonsensical_element
domain
domain_group
difficulty
difficulty_label
technique
is_control
```

### `ko_native_v0_1`

```text
id
domain
technique
difficulty
question
nonsensical_element
is_control
```

자체 제작본의 도메인, technique, 난이도 정의는 [`docs/TAXONOMY.md`](docs/TAXONOMY.md)에서 확인할 수 있습니다.

아직 작성되지 않은 native 행은 `id`만 유지하고 나머지 필드를 `null`로 둡니다. 한 행의 나머지 필드는 모두 채우거나 모두 `null`이어야 합니다.

## Native 문항 기여

팀원은 자신에게 배정된 placeholder 행을 채운 뒤 pull request를 올립니다.

1. 기존 `id`는 변경하지 않습니다.
2. `domain`, `technique`, `difficulty`, `question`, `nonsensical_element`, `is_control`을 모두 입력합니다.
3. 헛소리 요소가 포함된 현재 문항에서는 `is_control`을 `false`로 입력합니다.
4. 제출 전에 `python3 scripts/validate.py`를 실행합니다.

일부 필드만 채워진 행은 validator를 통과하지 않습니다.

## 사용 예시

GitHub의 JSONL 파일을 바로 불러올 수 있습니다.

```python
from datasets import load_dataset

native = load_dataset(
    "json",
    data_files={
        "test": "https://raw.githubusercontent.com/Hugging-Face-KREW/"
        "korean-bullshit-bench/main/data/ko_native_v0_1/test.jsonl"
    },
    split="test",
)
```

## 저장소 구조

```text
.
├── data/
│   ├── ko_native_v0_1/
│   │   └── test.jsonl
│   └── translated_v2/
│       └── test.jsonl
├── docs/
│   └── TAXONOMY.md
├── scripts/
│   ├── build_release.py
│   └── validate.py
├── LICENSE
├── LICENSES/
│   └── BullshitBench-LICENSE
├── NOTICE
├── README.md
└── benchmark.yaml
```

## 한계

- v0.1.0은 모든 문항에 의도적인 헛소리 전제가 포함되어 있습니다. 따라서 모델의 과잉 거절 경향은 이 데이터만으로 평가할 수 없습니다.
- `ko_native_v0_1`은 현재 8문항과 40개 기여용 placeholder로 구성되어 있습니다. 팀 기여가 완료되기 전에는 전체 native 벤치마크로 사용하면 안 됩니다.
- `translated_v2`는 번역 과정에서 원문의 난이도나 자연스러움이 달라질 수 있습니다.
- 공개된 벤치마크이므로 향후 모델 학습 데이터에 포함될 가능성이 있습니다.
- 법률, 의료, 금융 문항은 평가용으로 의도적인 오류를 포함하며 실제 조언으로 사용하면 안 됩니다.

## 원본 및 라이선스

`translated_v2`는 Peter Gostev의 [BullshitBench](https://github.com/petergpt/bullshit-benchmark) v2를 번역한 파생 데이터입니다. 원본 저작권과 MIT 라이선스는 [`NOTICE`](NOTICE)와 [`LICENSES/BullshitBench-LICENSE`](LICENSES/BullshitBench-LICENSE)에 보존되어 있습니다.

이 저장소 전체는 MIT 라이선스로 배포됩니다. 자세한 내용은 [`LICENSE`](LICENSE)를 참고하세요.

## Contributors

- 김원진
- 김준재
- 손지연
- 이효정
- 정소미
- 정우준
