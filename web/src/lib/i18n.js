// Language of the pages (French or English).
// Chosen from ?lang=fr|en, then the last choice (localStorage), then the browser language.

export const LANGS = ["fr", "en"];
const STORAGE_KEY = "openbeam-lang";

export function initialLang() {
  const asked = new URLSearchParams(window.location.search).get("lang");
  if (LANGS.includes(asked)) {
    saveLang(asked); // keep it when following links to the other pages
    return asked;
  }
  try {
    const saved = window.localStorage.getItem(STORAGE_KEY);
    if (LANGS.includes(saved)) return saved;
  } catch { /* storage unavailable */ }
  return (navigator.language || "fr").toLowerCase().startsWith("fr") ? "fr" : "en";
}

function saveLang(lang) {
  try { window.localStorage.setItem(STORAGE_KEY, lang); } catch { /* storage unavailable */ }
}

// A translatable text is either a plain string or { fr, en }.
export const tr = (text, lang) => (text == null || typeof text === "string" ? text : text[lang] ?? text.fr);

// Fill every [data-i18n="key"] element with strings[key].
export function translateStatic(strings, lang) {
  document.documentElement.lang = lang;
  document.querySelectorAll("[data-i18n]").forEach((el) => { el.textContent = tr(strings[el.dataset.i18n], lang); });
}

// Button showing the other language; calls onChange(lang) after switching.
export function mountLangToggle(button, lang, onChange) {
  let current = lang;
  const label = () => {
    const other = current === "fr" ? "en" : "fr";
    button.textContent = other.toUpperCase();
    button.title = other === "en" ? "Switch to English" : "Passer en français";
    button.setAttribute("aria-label", button.title);
  };
  label();
  button.addEventListener("click", () => {
    current = current === "fr" ? "en" : "fr";
    saveLang(current);
    label();
    onChange(current);
  });
}
