import re
from pathlib import Path

root = Path('.')
pages = [
    'Dennysmiskara (1).html',
    'MISKARA — Arabian Perfumes · Leave An Impression edited (1).html',
    'miskara_final (1).html',
    'miskara_athar.html',
    'miskara_body.html',
    'miskara_bakhur.html'
]

styles = []
js_outputs = {}
vendor_three = None

for page in pages:
    path = root / page
    if not path.exists():
        raise FileNotFoundError(page)
    text = path.read_text(encoding='utf-8')

    def style_repl(m):
        styles.append(m.group(0).replace('<style>', '').replace('</style>', ''))
        return ''

    text = re.sub(r'(?is)<style[^>]*>.*?</style>', style_repl, text)
    script_blocks = re.findall(r'(?is)<script(?:(?!src)[^>])*?>(.*?)</script>', text)
    text = re.sub(r'(?is)<script(?:(?!src)[^>])*?>.*?</script>', '', text)

    if page == 'MISKARA — Arabian Perfumes · Leave An Impression edited (1).html':
        if script_blocks:
            first = script_blocks[0]
            if 'THREE' in first[:1000] or '@license' in first[:1000] or 'function WebGL' in first[:1000]:
                vendor_three = first
                page_code = ''.join(script_blocks[1:])
            else:
                page_code = ''.join(script_blocks)
        else:
            page_code = ''
        js_outputs['main.js'] = page_code
    elif page == 'miskara_final (1).html':
        if script_blocks:
            first = script_blocks[0]
            if vendor_three is None and ('THREE' in first[:1000] or '@license' in first[:1000] or 'function WebGL' in first[:1000]):
                vendor_three = first
            page_code = ''.join(script_blocks[1:] if len(script_blocks) > 1 else script_blocks)
        else:
            page_code = ''
        js_outputs['miskara_final.js'] = page_code
    elif page == 'miskara_athar.html':
        js_outputs['miskara_athar.js'] = ''.join(script_blocks)
    elif page == 'miskara_body.html':
        js_outputs['miskara_body.js'] = ''.join(script_blocks)
    elif page == 'miskara_bakhur.html':
        js_outputs['miskara_bakhur.js'] = ''.join(script_blocks)
    elif page == 'Dennysmiskara (1).html':
        js_outputs['landing.js'] = ''.join(script_blocks)

    if '<link rel="stylesheet" href="styles.css">' not in text:
        text = re.sub(r'(<meta[^>]*name="viewport"[^>]*>)(\s*)', r"\1\2<link rel=\"stylesheet\" href=\"styles.css\">\2", text, count=1, flags=re.I)
    inserts = []
    if page == 'MISKARA — Arabian Perfumes · Leave An Impression edited (1).html':
        if vendor_three is not None:
            inserts.append('<script src="three.js"></script>')
        inserts.append('<script src="main.js"></script>')
    elif page == 'miskara_final (1).html':
        if vendor_three is not None:
            inserts.append('<script src="three.js"></script>')
        inserts.append('<script src="miskara_final.js"></script>')
    elif page == 'miskara_athar.html':
        inserts.append('<script src="miskara_athar.js"></script>')
    elif page == 'miskara_body.html':
        inserts.append('<script src="miskara_body.js"></script>')
    elif page == 'miskara_bakhur.html':
        inserts.append('<script src="miskara_bakhur.js"></script>')
    elif page == 'Dennysmiskara (1).html':
        inserts.append('<script src="landing.js"></script>')
    if inserts:
        if '</body>' in text:
            text = text.replace('</body>', '\n  ' + '\n  '.join(inserts) + '\n</body>')
        else:
            text += '\n' + '\n'.join(inserts)
    path.write_text(text, encoding='utf-8')

Path('styles.css').write_text('\n'.join(s.strip() for s in styles if s.strip()) + '\n', encoding='utf-8')
for name, code in js_outputs.items():
    Path(name).write_text(code.strip() + '\n', encoding='utf-8')
if vendor_three is not None:
    Path('three.js').write_text(vendor_three.strip() + '\n', encoding='utf-8')
print(f'finished {len(styles)} style blocks and wrote {len(js_outputs)} JS files; vendor_three={vendor_three is not None}')
