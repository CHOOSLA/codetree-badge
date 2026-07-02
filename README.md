# codetree-badge

코드트리(Codetree) 학습 진도를 SVG 뱃지로 만들어 README 에 붙일 수 있게 해주는 프로젝트입니다. fork 후 본인 계정 정보를 Secrets 에 넣으면 GitHub Actions 가 매시간 `result/` 의 SVG 를 갱신합니다.

## 사용법

1. 이 저장소를 fork 합니다.
2. Settings → Secrets and variables → Actions 에 `CODETREE_ID`, `CODETREE_PW`, `CODETREE_DEVICE_INFO` 를 등록합니다.
3. Actions 탭에서 워크플로를 활성화하고 한 번 수동 실행합니다.

README 에는 아래처럼 붙입니다.

```markdown
![Codetree Summary](https://raw.githubusercontent.com/{username}/codetree-badge/main/result/summary.svg)
```

로컬에서 샘플 데이터로 미리 보려면:

```bash
python src/generate.py --sample
```

## License

MIT
