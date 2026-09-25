"""Bouwt de designpagina's: voegt gedeelde header/footer in en inlinet de logo-SVG's met unieke id's."""
import re

color = open('logo-color.clean.svg').read()
white = open('logo-white.clean.svg').read()


def reid(s, old, new):
    return re.sub(r'(id="|url\(#)' + old, lambda m: m.group(1) + new, s)


LOGOS = {
    '{{LOGO_REV}}': reid(color.replace('fill: #1d1d1b', 'fill: #fff'), 'lc', 'lr'),
    '{{LOGO_WHITE_D}}': reid(white, 'lw', 'wd').replace('aria-label="Triple R"', 'aria-hidden="true"'),
    '{{LOGO_WHITE_F}}': reid(white, 'lw', 'wf'),
    '{{LOGO_WHITE_H}}': reid(white, 'lw', 'wh'),
    '{{LOGO_COLOR_D}}': reid(color, 'lc', 'ld').replace('aria-label="Triple R"', 'aria-hidden="true"'),
    '{{LOGO_COLOR}}': color,
}
HEADER = open('partials/header.html').read()
FOOTER = open('partials/footer.html').read()
PAGES = ['homepage', 'producten', 'besparingscalculator', 'design-system']
HEAD = ('<!doctype html>\n<html lang="nl">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n')

for name in PAGES:
    try:
        src = open(f'{name}.src.html').read()
    except FileNotFoundError:
        continue
    src = src.replace('{{HEADER}}', HEADER).replace('{{FOOTER}}', FOOTER)
    for k, v in LOGOS.items():
        src = src.replace(k, v)
    i = src.index('</style>') + len('</style>')
    open(f'{name}.html', 'w').write(HEAD + src[:i] + '\n</head>\n<body>\n' + src[i:] + '\n</body>\n</html>\n')
    print(f'{name}.html')
