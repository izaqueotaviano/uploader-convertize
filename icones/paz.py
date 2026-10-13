#!/usr/bin/env python3
"""VectorCraft, opção 4: mão fazendo "V" com dois lápis no lugar dos dedos, traço preto grosso,
fundo amarelo. Desenho original no estilo flat/cartoon.

    python3 icones/paz.py
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gerar_icones import SQ, icon  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
INK, PAPER = "#15151a", "#ffffff"
BG, LEAD, ERASER, WOOD = "#f7b928", "#ffe14d", "#ff6f7d", "#fde9c6"
SW = 30  # espessura do traço


def pencil(x, y, angle, length, tip):
    """Lápis vertical de largura 120 com base em (x, y), girado `angle` graus em torno da base.
    tip=True: ponta apontada para cima; False: borracha para cima."""
    w, hw = 120, 60
    top = y - length
    g = [f'<g transform="rotate({angle} {x} {y})">']
    body_top = top + 150
    # corpo
    g.append(f'<rect x="{x-hw}" y="{body_top}" width="{w}" height="{y-body_top+40}" fill="{LEAD}"/>')
    g.append(f'<line x1="{x-20}" y1="{body_top+10}" x2="{x-20}" y2="{y+30}" stroke="{INK}" stroke-width="12"/>')
    g.append(f'<line x1="{x+20}" y1="{body_top+10}" x2="{x+20}" y2="{y+30}" stroke="{INK}" stroke-width="12"/>')
    if tip:
        # madeira apontada + grafite
        g.append(f'<path d="M{x-hw},{body_top} L{x},{top} L{x+hw},{body_top} Z" fill="{WOOD}"/>')
        g.append(f'<path d="M{x-hw},{body_top} L{x},{top} L{x+hw},{body_top}" fill="none" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"/>')
        g.append(f'<path d="M{x-26},{top+74} L{x},{top+8} L{x+26},{top+74} Z" fill="{INK}"/>')
        g.append(f'<line x1="{x-hw}" y1="{body_top}" x2="{x+hw}" y2="{body_top}" stroke="{INK}" stroke-width="{SW}"/>')
    else:
        # borracha + virola com duas faixas
        g.append(f'<rect x="{x-hw}" y="{top}" width="{w}" height="80" rx="26" fill="{ERASER}"/>')
        g.append(f'<rect x="{x-hw}" y="{top+60}" width="{w}" height="90" fill="{PAPER}"/>')
        g.append(f'<line x1="{x-hw}" y1="{top+60}" x2="{x+hw}" y2="{top+60}" stroke="{INK}" stroke-width="{SW}"/>')
        g.append(f'<line x1="{x-hw}" y1="{top+105}" x2="{x+hw}" y2="{top+105}" stroke="{INK}" stroke-width="{SW}"/>')
        g.append(f'<line x1="{x-hw}" y1="{body_top}" x2="{x+hw}" y2="{body_top}" stroke="{INK}" stroke-width="{SW}"/>')
        g.append(f'<rect x="{x-hw}" y="{top}" width="{w}" height="{150}" rx="26" fill="none" stroke="{INK}" stroke-width="{SW}"/>')
    # contorno do corpo (lados)
    g.append(f'<line x1="{x-hw}" y1="{body_top}" x2="{x-hw}" y2="{y+40}" stroke="{INK}" stroke-width="{SW}"/>')
    g.append(f'<line x1="{x+hw}" y1="{body_top}" x2="{x+hw}" y2="{y+40}" stroke="{INK}" stroke-width="{SW}"/>')
    g.append("</g>")
    return "".join(g)


def vc_paz():
    o = f'stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round" stroke-linecap="round"'
    # punho redondo, polegar cruzando, dois dedos dobrados por cima do polegar
    fist = ("M300,640 C300,520 390,440 520,440 L600,440 C720,440 800,530 800,660 "
            "L800,700 C800,830 710,910 580,910 L520,910 C390,910 300,830 300,720 Z")
    body = f"""
<path d="{SQ}" fill="{BG}"/>
<g transform="translate(512 520) scale(0.84) translate(-512 -520)">
{pencil(492, 610, -20, 520, False)}
{pencil(592, 610, 20, 540, True)}
<path d="{fist}" fill="{PAPER}" {o}/>
<g transform="rotate(-14 620 600)"><rect x="470" y="548" width="285" height="104" rx="52" fill="{PAPER}" {o}/></g>
<rect x="330" y="540" width="84" height="240" rx="42" fill="{PAPER}" {o}/>
<rect x="438" y="518" width="88" height="270" rx="44" fill="{PAPER}" {o}/>
<path d="M590,775 C640,762 700,764 735,784" fill="none" {o}/>
</g>
"""
    return icon("", BG, body, glass=False)


if __name__ == "__main__":
    out = os.path.join(HERE, "opcoes", "vectorcraft-4-paz.svg")
    with open(out, "w") as f:
        f.write(vc_paz())
    subprocess.run(["resvg", "-w", "1024", out, out[:-4] + ".png"], check=True)
    print(out)
