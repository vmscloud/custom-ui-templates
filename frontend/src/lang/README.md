# DEPRECATED — 사용하지 않는 폴더

`ko.json` · `en.json` · `zh.json` · `jp.json` 은 **deprecated** 입니다. 어떤 코드도 이 파일을 읽지 않으며, 폴백으로도 쓰이지 않습니다.

- dev 단독 실행의 번역은 개발자 도구 설정의 프로젝트 ID·언어로 systemmanagement 용어관리(DB)에서 받습니다 (`src/plugins/i18n.ts` 의 `loadLanguageFromHost`).
- 번역이 없는 키는 키 이름 그대로 표시됩니다. 이 JSON 에 추가하지 말고 **용어관리(DB)에 등록**하세요.
- 이 파일들은 수정하지 마세요. 값은 마지막 사용 시점 그대로이며 DB 와 이미 다릅니다.
