const CACHE_PREFIX = "kalu-catalogo-pwa-";
const SHELL_CACHE = CACHE_PREFIX + "shell-v13";
const RUNTIME_CACHE = CACHE_PREFIX + "runtime-v13";
const MAX_RUNTIME_ENTRIES = 100;
const APP_SCOPE = new URL(self.registration.scope);
const INDEX_URL = new URL("index.html", APP_SCOPE).href;
const SHELL_URLS = [
  new URL("./", APP_SCOPE).href,
  INDEX_URL,
  new URL("styles.min.css?v=49", APP_SCOPE).href,
  new URL("app.min.js?v=41", APP_SCOPE).href,
  new URL("pwa.js?v=1", APP_SCOPE).href,
  new URL("manifest.webmanifest", APP_SCOPE).href,
  new URL("assets/pwa-icon-192.png", APP_SCOPE).href,
  new URL("assets/pwa-icon-512.png", APP_SCOPE).href
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(SHELL_CACHE)
      .then((cache) => cache.addAll(SHELL_URLS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) =>
        Promise.all(
          keys
            .filter((key) => key.startsWith(CACHE_PREFIX) && key !== SHELL_CACHE && key !== RUNTIME_CACHE)
            .map((key) => caches.delete(key))
        )
      )
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  if (url.origin !== APP_SCOPE.origin || !url.pathname.startsWith(APP_SCOPE.pathname)) return;

  const isAppShellResource = ["document", "script", "style", "manifest"].includes(request.destination);
  event.respondWith(isAppShellResource ? networkFirst(request) : cacheFirst(request));
});

async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok && response.type === "basic") await storeRuntimeResponse(request, response.clone());
    return response;
  } catch {
    const cached = await caches.match(request);
    if (cached) return cached;

    if (request.mode === "navigate") {
      const appShell = await caches.match(INDEX_URL);
      if (appShell) return appShell;
    }

    return new Response("Sin conexi\u00f3n. Intenta de nuevo cuando tengas internet.", {
      status: 503,
      headers: { "Content-Type": "text/plain; charset=utf-8" }
    });
  }
}

async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;

  try {
    const response = await fetch(request);
    if (response.ok && response.type === "basic") await storeRuntimeResponse(request, response.clone());
    return response;
  } catch {
    return new Response("", { status: 504, statusText: "Offline" });
  }
}

async function storeRuntimeResponse(request, response) {
  const cache = await caches.open(RUNTIME_CACHE);
  await cache.put(request, response);
  const keys = await cache.keys();
  const expired = keys.slice(0, Math.max(0, keys.length - MAX_RUNTIME_ENTRIES));
  await Promise.all(expired.map((key) => cache.delete(key)));
}