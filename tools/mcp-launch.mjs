#!/usr/bin/env node
// MCP 서버 런처 — 비밀정보를 .env 에서 주입하기 위한 얇은 래퍼.
//
// 배경: Claude Code 는 .mcp.json 의 ${VAR} 를 "claude 를 띄운 셸의 환경"에서만 읽고,
//       .env 를 자동 로드하지 않는다. 그래서 토큰/DB 비밀번호 같은 값을 커밋되는
//       .mcp.json 에 직접 적지 않으려면, 이 런처가 프로젝트 루트의 .env 를 읽어
//       환경에 주입한 뒤 실제 MCP 서버 프로세스로 위임한다.
//
// 사용법(.mcp.json):
//   node tools/mcp-launch.mjs -- <command> [args...]
//   - '--' 뒤가 실제 실행 대상.
//   - 인자에 들어있는 {{VAR}} 토큰은 .env 값으로 치환된다.
//     ({{...}} 구문을 쓰는 이유: Claude Code 의 ${...} 확장과 충돌하지 않도록.)
//   - child 는 stdio 를 그대로 상속하므로 MCP stdio(JSON-RPC) 가 투명하게 전달된다.

import { spawn } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const projectRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');

// --- .env 로드 (KEY=VALUE, # 주석, 양끝 따옴표 제거; 기존 환경변수가 우선) ---
function loadEnv(file) {
  let text;
  try {
    text = readFileSync(file, 'utf8');
  } catch {
    return; // 파일 없으면 조용히 통과
  }
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trim();
    if (!line || line.startsWith('#')) continue;
    const eq = line.indexOf('=');
    if (eq === -1) continue;
    const key = line.slice(0, eq).trim();
    let val = line.slice(eq + 1).trim();
    if (
      (val.startsWith('"') && val.endsWith('"')) ||
      (val.startsWith("'") && val.endsWith("'"))
    ) {
      val = val.slice(1, -1);
    }
    if (!(key in process.env)) process.env[key] = val;
  }
}
loadEnv(resolve(projectRoot, '.env'));
loadEnv(resolve(projectRoot, '.env.local')); // 로컬 오버라이드(선택)

// --- '--' 뒤의 실제 실행 대상 파싱 ---
const sep = process.argv.indexOf('--');
if (sep === -1) {
  console.error('[mcp-launch] "--" 구분자가 필요합니다: node mcp-launch.mjs -- <command> [args...]');
  process.exit(2);
}

function expandTokens(s) {
  return s.replace(/\{\{([A-Z0-9_]+)\}\}/g, (_m, name) => {
    const v = process.env[name];
    if (v === undefined || v === '') {
      console.error(`[mcp-launch] 환경변수 ${name} 가 설정되지 않았습니다. 프로젝트 루트의 .env 를 확인하세요 (.env.example 참고).`);
      process.exit(3);
    }
    return v;
  });
}

const rest = process.argv.slice(sep + 1).map(expandTokens);
if (rest.length === 0) {
  console.error('[mcp-launch] 실행할 명령이 없습니다.');
  process.exit(2);
}

// 대상이 node 면 동일한 node 실행파일을 사용해 버전 불일치를 방지
let [cmd, ...args] = rest;
if (cmd === 'node') cmd = process.execPath;

const child = spawn(cmd, args, { stdio: 'inherit', env: process.env });
child.on('error', (e) => {
  console.error('[mcp-launch] 실행 실패:', e.message);
  process.exit(1);
});
child.on('exit', (code, signal) => {
  process.exit(code ?? (signal ? 1 : 0));
});
