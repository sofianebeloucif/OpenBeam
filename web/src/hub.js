// Hub page: one card per beam of the registry, in French or English.

import { BEAMS } from "./beams.js";
import { initialLang, mountLangToggle, tr, translateStatic } from "./lib/i18n.js";
import { HUB_STRINGS as S } from "./lib/strings.js";

function element(tag, props = {}, ...children) {
  const node = Object.assign(document.createElement(tag), props);
  node.append(...children.filter((c) => c != null));
  return node;
}

function card(beam, lang) {
  const ready = beam.status === "ready";
  const visual = beam.thumbnail
    ? element("img", { src: beam.thumbnail, alt: "", loading: "lazy" })
    : element("div", { className: `placeholder placeholder-${beam.id}` });
  const body = element(
    "div", { className: "card-body" },
    element("h2", { textContent: tr(beam.title, lang) }),
    element("p", { textContent: tr(beam.summary, lang) }),
    element("ul", { className: "tags" }, ...beam.tags.map((t) => element("li", { textContent: tr(t, lang) }))),
    element(
      "div", { className: "card-footer" },
      beam.reference
        ? element("a", { className: "reference", href: beam.reference.href, textContent: beam.reference.label })
        : element("span"),
      element("span", { className: `action ${ready ? "" : "disabled"}`, textContent: tr(ready ? S.explore : S.soon, lang) }),
    ),
  );
  const media = element("div", { className: "card-media" }, visual);
  if (!ready) return element("article", { className: "card soon", ariaDisabled: "true" }, media, body);
  // the whole card is the link; the reference link stays clickable on top of it
  const link = element("a", { className: "card-link", href: beam.href, ariaLabel: `${tr(S.open, lang)} ${tr(beam.title, lang)}` });
  return element("article", { className: "card" }, link, media, body);
}

function render(lang) {
  translateStatic(S, lang);
  document.title = `OpenBeam : ${tr(S.heading, lang)}`;
  document.getElementById("beams").setAttribute("aria-label", tr(S.beamsLabel, lang));
  document.getElementById("beams").replaceChildren(...BEAMS.map((beam) => card(beam, lang)));
}

const lang = initialLang();
render(lang);
mountLangToggle(document.getElementById("lang"), lang, render);
