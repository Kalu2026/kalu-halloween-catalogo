(() => {
  const installButton = document.getElementById("pwa-install-button");
  const canonicalLink = document.querySelector('link[rel="canonical"]');
  const appBase = canonicalLink ? new URL(canonicalLink.href) : new URL("./", window.location.href);

  if ("serviceWorker" in navigator && window.isSecureContext) {
    navigator.serviceWorker
      .register(new URL("service-worker.js", appBase).href, { scope: appBase.pathname })
      .catch(() => {});
  }

  if (!installButton) return;

  const isIOS =
    /iPad|iPhone|iPod/i.test(navigator.userAgent) ||
    (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  const isAlreadyInstalled = window.navigator.standalone === true;
  let deferredPrompt = null;

  if (isIOS && !isAlreadyInstalled) {
    installButton.hidden = false;
    installButton.textContent = "C\u00f3mo instalar";
  }

  installButton.addEventListener("click", async () => {
    if (deferredPrompt) {
      const prompt = deferredPrompt;
      deferredPrompt = null;
      await prompt.prompt();
      const choice = await prompt.userChoice;
      if (choice.outcome === "accepted") installButton.hidden = true;
      return;
    }

    if (isIOS) {
      window.alert(
        "Para instalar Kal\u00fa en tu iPhone o iPad: abre esta p\u00e1gina en Safari, toca Compartir y elige Agregar a pantalla de inicio."
      );
    }
  });

  window.addEventListener("beforeinstallprompt", (event) => {
    event.preventDefault();
    deferredPrompt = event;
    installButton.textContent = "Instalar app";
    installButton.hidden = false;
  });

  window.addEventListener("appinstalled", () => {
    deferredPrompt = null;
    installButton.hidden = true;
  });
})();