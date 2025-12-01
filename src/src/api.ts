// api.ts - fetch wrapper to include JWT as Bearer token

import { userStore } from "./stores/UserStore";

export async function apiFetch(input: RequestInfo, init: RequestInit = {}) {
  const headers = new Headers(init.headers || {});
  if (userStore.jwt) {
    headers.set("Authorization", `Bearer ${userStore.jwt}`);
  }
  // Always set Content-Type for JSON if not set and body is present
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  return fetch(input, { ...init, headers });
}