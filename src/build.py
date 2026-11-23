"""Monta las páginas de consejos a partir de los textos en src/consejos/.
Cada consejo es un .html con cabecera de datos entre <!-- y --> :
  slug, titulo, resumen, etiqueta, fecha (AAAA-MM-DD)
Uso: python3 build.py <carpeta_src> <carpeta_web>
"""
import sys, pathlib, re, html

SITE = "https://osmar-rotela-electricista.netlify.app"
src = pathlib.Path(sys.argv[1]); web = pathlib.Path(sys.argv[2])

HEAD = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:locale" content="es_ES">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="https://osmar-rotela-electricista.netlify.app/og-osmar.jpg">
<meta name="twitter:card" content="summary_large_image">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/estilo.css">
{ld}
</head>
<body>
<header class="top">
<div class="wrap">
<a class="brand" href="/"><span class="bolt"><svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#17365d" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 4 14h7l-1 8 9-12h-7l1-8z"/></svg></span>Osmar Rotela</a>
<nav aria-label="Secciones">
<a class="hide-sm" href="/#servicios">Servicios</a>
<a href="/consejos/">Consejos</a>
<a href="/#contacto">Contacto</a>
</nav>
</div>
</header>
"""

CTA = """<div class="cta">
<h2>{cta_title}</h2>
<p>Trabajo en Málaga capital por las tardes y los sábados. Mándame una foto por WhatsApp y te digo qué puede ser.</p>
<div class="btns">
<a class="btn btn-wa" href="https://wa.me/34631400753">Escríbeme por WhatsApp</a>
<a class="btn btn-tel" href="tel:+34631400753">Llamar · 631 400 753</a>
</div>
</div>
"""

FOOT = """<footer>
<div class="wrap">Osmar Rotela – Electricidad y Mantenimiento · Málaga · <a href="tel:+34631400753">631 400 753</a> · <a href="/consejos/">Consejos</a></div>
</footer>
</body>
</html>
"""

def meta(text):
    m = re.match(r"\s*<!--(.*?)-->", text, re.S)
    data = {}
    for line in m.group(1).strip().splitlines():
        k, v = line.split(":", 1)
        data[k.strip()] = v.strip()
    return data, text[m.end():]

articles = []
for f in sorted((src / "consejos").glob("*.html")):
    d, body = meta(f.read_text(encoding="utf-8"))
    d["body"] = body
    articles.append(d)
articles.sort(key=lambda a: a["fecha"], reverse=True)

for a in articles:
    url = f"{SITE}/consejos/{a['slug']}/"
    import json
    ld = '<script type="application/ld+json">' + json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": a["titulo"], "description": a["resumen"],
        "datePublished": a["fecha"], "inLanguage": "es", "mainEntityOfPage": url,
        "author": {"@type": "Person", "name": "Osmar Rotela"},
        "publisher": {"@type": "Organization", "name": "Osmar Rotela – Electricidad y Mantenimiento"}
    }, ensure_ascii=False) + '</script>'
    page = HEAD.format(title=html.escape(a["titulo"]) + " | Osmar Rotela, electricista en Málaga",
                       desc=html.escape(a["resumen"]), url=url, ld=ld)
    page += f"""<div class="art-head"><div class="wrap narrow">
<div class="crumbs"><a href="/">Inicio</a> › <a href="/consejos/">Consejos</a></div>
<h1>{html.escape(a['titulo'])}</h1>
<p>{html.escape(a['resumen'])}</p>
</div></div>
<main class="wrap narrow"><article>
{a['body']}
</article>
{CTA.format(cta_title=a.get('cta', '¿No lo encuentras o no te quedas tranquilo?'))}
</main>
""" + FOOT
    out = web / "consejos" / a["slug"]
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page, encoding="utf-8")

# Lista de consejos
cards = "\n".join(
    f'<a class="tip" href="/consejos/{a["slug"]}/"><span class="tag">{html.escape(a["etiqueta"])}</span>'
    f'<h3>{html.escape(a["titulo"])}</h3><p>{html.escape(a["resumen"])}</p><span class="more">Leer →</span></a>'
    for a in articles)
lista = HEAD.format(title="Consejos de electricidad para casa | Osmar Rotela, electricista en Málaga",
                    desc="Consejos sencillos de electricidad para casa: por qué salta el diferencial, qué es cada palanca del cuadro, antenas y más. Escritos por un electricista de Málaga.",
                    url=f"{SITE}/consejos/", ld="")
lista += f"""<div class="art-head"><div class="wrap">
<div class="crumbs"><a href="/">Inicio</a> › Consejos</div>
<h1>Consejos de electricidad para casa</h1>
<p>Lo que más me preguntan, explicado claro. Cosas que puedes comprobar tú sin peligro y cuándo es mejor llamar.</p>
</div></div>
<main class="wrap" style="padding:40px 20px 0">
<div class="tips">
{cards}
</div>
{CTA.format(cta_title='¿Tienes una avería ahora?')}
</main>
""" + FOOT
(web / "consejos").mkdir(exist_ok=True)
(web / "consejos" / "index.html").write_text(lista, encoding="utf-8")

# sitemap y robots
latest = articles[0]["fecha"] if articles else ""
urls = [(f"{SITE}/", latest), (f"{SITE}/consejos/", latest)] + \
       [(f"{SITE}/consejos/{a['slug']}/", a["fecha"]) for a in articles]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
sm += "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls)
sm += "</urlset>\n"
(web / "sitemap.xml").write_text(sm, encoding="utf-8")
(web / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /capi/\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
print("Consejos:", [a["slug"] for a in articles])
