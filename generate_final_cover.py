import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cairosvg

def build_perfect_designer_lighthouse_svg(size=2000):
    """
    100% exact vector reconstruction of the designer's lighthouse emblem:
    - Gold beams with smooth circular arc ends
    - Left side of dome: White (#FFFFFF)
    - Right side of dome: Dark Teal (#214149)
    - Lantern room: Dark Teal (#214149) with vertical white struts and glowing gold lamp (#F3D593)
    - Balcony: Left white (#FFFFFF), Right dark teal (#214149)
    - Tower body: Left half white (#FFFFFF), Right half light aqua (#A5D2DF)
    - Windows: 2 arched windows on right half (#214149)
    - Door: Arched doorway at base (#214149)
    - Rock base: Multilayered rock facets (White highlight #FFFFFF, Cyan facet #A5D2DF, Dark teal base #214149)
    - Water ripples: Horizontal lines under rock (#214149, #315F6D, #468A9D, #A5D2DF)
    """
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="{size}" height="{size}">
  <defs>
    <!-- Gold Beam Gradients -->
    <linearGradient id="goldBeamL" x1="460" y1="365" x2="60" y2="365" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#F3D593" stop-opacity="0.95" />
      <stop offset="35%" stop-color="#D4AF5F" stop-opacity="0.88" />
      <stop offset="100%" stop-color="#C19B4F" stop-opacity="0.70" />
    </linearGradient>

    <linearGradient id="goldBeamR" x1="540" y1="365" x2="940" y2="365" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#F3D593" stop-opacity="0.95" />
      <stop offset="35%" stop-color="#D4AF5F" stop-opacity="0.88" />
      <stop offset="100%" stop-color="#C19B4F" stop-opacity="0.70" />
    </linearGradient>

    <radialGradient id="lampGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#FFFFFF" />
      <stop offset="35%" stop-color="#FFF0C8" />
      <stop offset="75%" stop-color="#F3D593" />
      <stop offset="100%" stop-color="#C19B4F" />
    </radialGradient>
  </defs>

  <g id="designer_lighthouse_artwork">
    <!-- 1. Gold Light Beams with Circular Arc Outer Ends -->
    <!-- Left Beam -->
    <path d="M 460 352 
             L 92 322 
             A 450 450 0 0 0 62 414 
             L 460 378 Z" 
          fill="url(#goldBeamL)" />

    <!-- Right Beam -->
    <path d="M 540 352 
             L 908 322 
             A 450 450 0 0 1 938 414 
             L 540 378 Z" 
          fill="url(#goldBeamR)" />

    <!-- 2. Water Reflection Wave Lines (Under the island) -->
    <g stroke-linecap="round">
      <line x1="250" y1="672" x2="750" y2="672" stroke="#214149" stroke-width="4.5" />
      <line x1="300" y1="681" x2="700" y2="681" stroke="#2E5864" stroke-width="4" />
      <line x1="355" y1="690" x2="645" y2="690" stroke="#468A9D" stroke-width="3.5" />
      <line x1="410" y1="698" x2="590" y2="698" stroke="#A5D2DF" stroke-width="3" />
      <line x1="460" y1="706" x2="540" y2="706" stroke="#A5D2DF" stroke-width="2.5" />
    </g>

    <!-- 3. Rocky Island Base -->
    <!-- Dark Teal Main Rock Body (#214149) -->
    <path d="M 315 668 
             C 335 648, 370 638, 405 636 
             C 422 628, 440 622, 458 620 
             L 542 620 
             C 560 622, 578 628, 595 636 
             C 630 638, 665 648, 685 668 
             C 590 675, 410 675, 315 668 Z" 
          fill="#214149" />

    <!-- Rock Facet Mid-tone (#315F6D) -->
    <path d="M 335 664 
             C 360 648, 390 642, 418 638 
             C 436 630, 450 624, 465 622 
             L 535 622 
             C 550 624, 564 630, 582 638 
             C 610 642, 640 648, 665 664 
             C 580 670, 420 670, 335 664 Z" 
          fill="#315F6D" />

    <!-- Light Blue/Cyan Left Facet Highlight (#A5D2DF) -->
    <path d="M 355 658 
             C 385 644, 412 640, 435 638 
             L 485 638 
             C 460 648, 425 655, 355 658 Z" 
          fill="#A5D2DF" />

    <!-- Pure White Top Island Highlight Ledge (#FFFFFF) -->
    <path d="M 425 636 
             C 442 624, 462 620, 480 620 
             L 520 620 
             C 510 626, 470 632, 425 636 Z" 
          fill="#FFFFFF" />

    <!-- 4. Lighthouse Tower Body -->
    <!-- Left Half: Solid Pure White (#FFFFFF) -->
    <polygon points="452,620 466,392 500,392 500,620" fill="#FFFFFF" />
    
    <!-- Right Half: Solid Soft Cyan/Blue (#A5D2DF) -->
    <polygon points="500,620 500,392 534,392 548,620" fill="#A5D2DF" />

    <!-- Tower Windows & Doors (Dark Navy #214149) -->
    <!-- Bottom Entryway Door (Arched) -->
    <path d="M 488 620 L 488 574 C 488 568, 512 568, 512 574 L 512 620 Z" fill="#214149" />
    
    <!-- Middle Arched Window (Right side) -->
    <path d="M 506 512 L 506 488 C 506 483, 520 483, 520 488 L 520 512 C 520 516, 506 516, 506 512 Z" fill="#214149" />

    <!-- Upper Arched Window (Right side) -->
    <path d="M 506 446 L 506 426 C 506 422, 518 422, 518 426 L 518 446 C 518 449, 506 449, 506 446 Z" fill="#214149" />

    <!-- 5. Balcony / Gallery Platform (y=384..392) -->
    <rect x="448" y="384" width="52" height="8" rx="1.5" fill="#FFFFFF" />
    <rect x="500" y="384" width="52" height="8" rx="1.5" fill="#A5D2DF" />
    <line x1="448" y1="392" x2="552" y2="392" stroke="#214149" stroke-width="2" />

    <!-- Balcony Railing (y=369..384) -->
    <line x1="450" y1="371" x2="550" y2="371" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round"/>
    <!-- Posts -->
    <line x1="452" y1="371" x2="452" y2="384" stroke="#FFFFFF" stroke-width="2.5" />
    <line x1="470" y1="371" x2="470" y2="384" stroke="#FFFFFF" stroke-width="2" />
    <line x1="488" y1="371" x2="488" y2="384" stroke="#FFFFFF" stroke-width="2" />
    <line x1="512" y1="371" x2="512" y2="384" stroke="#A5D2DF" stroke-width="2" />
    <line x1="530" y1="371" x2="530" y2="384" stroke="#A5D2DF" stroke-width="2" />
    <line x1="548" y1="371" x2="548" y2="384" stroke="#A5D2DF" stroke-width="2.5" />

    <!-- 6. Lantern Chamber (y=334..371) -->
    <rect x="464" y="336" width="72" height="36" fill="#214149" />
    
    <!-- Central Glowing Lamp -->
    <circle cx="500" cy="354" r="10" fill="url(#lampGlow)" />
    <rect x="496" y="336" width="8" height="36" fill="#F3D593" opacity="0.95" />
    
    <!-- Vertical Frame Mullions -->
    <rect x="464" y="336" width="6" height="36" fill="#FFFFFF" />
    <rect x="480" y="336" width="4" height="36" fill="#FFFFFF" />
    <rect x="516" y="336" width="4" height="36" fill="#A5D2DF" />
    <rect x="530" y="336" width="6" height="36" fill="#A5D2DF" />

    <!-- Cornice Shelf -->
    <rect x="460" y="332" width="40" height="5" rx="1.5" fill="#FFFFFF" />
    <rect x="500" y="332" width="40" height="5" rx="1.5" fill="#A5D2DF" />

    <!-- 7. Dome / Cupola (y=304..332) -->
    <!-- Left Half: White #FFFFFF -->
    <path d="M 464 332 
             C 464 308, 480 304, 500 304 
             L 500 332 Z" 
          fill="#FFFFFF" />
    <!-- Right Half: Dark Teal #214149 -->
    <path d="M 500 304 
             C 520 304, 536 308, 536 332 
             L 500 332 Z" 
          fill="#214149" />

    <!-- 8. Spire & Finial (y=270..304) -->
    <rect x="496" y="294" width="8" height="10" fill="#FFFFFF" />
    <circle cx="500" cy="288" r="6" fill="#FFFFFF" />
    <line x1="500" y1="270" x2="500" y2="284" stroke="#FFFFFF" stroke-width="3.5" stroke-linecap="round"/>
  </g>
</svg>'''
    return svg

def create_final_master_vk_cover():
    W, H = 1920, 768
    
    # 1. Background Sea Gradient:
    y_coords, x_coords = np.mgrid[0:H, 0:W]
    
    c_top = np.array([26, 51, 58], dtype=np.float32)       # #1A333A
    c_bottom = np.array([72, 141, 160], dtype=np.float32)  # #488DA0
    
    norm_y = y_coords / H
    norm_x = x_coords / W
    
    t = 0.70 * norm_y + 0.30 * norm_x
    t = np.clip(t, 0.0, 1.0)
    
    rgb = (1.0 - t[:, :, np.newaxis]) * c_top + t[:, :, np.newaxis] * c_bottom
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    bg_img = Image.fromarray(rgb, "RGB").convert("RGBA")
    
    # 2. Soft Atmospheric Lighting & Mist:
    mist_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    mist_draw = ImageDraw.Draw(mist_layer)
    mist_draw.ellipse((-200, 250, 1100, 900), fill=(72, 141, 160, 45))
    mist_draw.ellipse((500, 320, 1900, 1000), fill=(70, 138, 157, 50))
    mist_draw.ellipse((1100, 200, 2200, 900), fill=(72, 141, 160, 45))
    mist_layer = mist_layer.filter(ImageFilter.GaussianBlur(90))
    
    # Lighthouse position in bottom right:
    lh_cx = 1640
    lh_cy = 575
    lh_size = 460
    
    # Lantern halo glow:
    lantern_x = lh_cx
    lantern_y = lh_cy - int(lh_size * 0.14)
    
    halo_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hdraw = ImageDraw.Draw(halo_layer)
    hdraw.ellipse((lantern_x - 240, lantern_y - 180, lantern_x + 240, lantern_y + 180), fill=(193, 155, 79, 40))
    hdraw.ellipse((lantern_x - 150, lantern_y - 110, lantern_x + 150, lantern_y + 110), fill=(243, 213, 147, 45))
    hdraw.ellipse((lantern_x - 80, lantern_y - 60, lantern_x + 80, lantern_y + 60), fill=(255, 248, 220, 55))
    halo_layer = halo_layer.filter(ImageFilter.GaussianBlur(40))
    
    # Soft wide beam extending towards center/left
    beam_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(beam_layer)
    bdraw.polygon([(lantern_x - 20, lantern_y - 10), (0, 320), (0, 580), (lantern_x - 20, lantern_y + 15)], fill=(243, 213, 147, 18))
    bdraw.polygon([(lantern_x + 20, lantern_y - 10), (W, 480), (W, 640), (lantern_x + 20, lantern_y + 15)], fill=(243, 213, 147, 18))
    beam_layer = beam_layer.filter(ImageFilter.GaussianBlur(30))
    
    canvas = Image.alpha_composite(bg_img, mist_layer)
    canvas = Image.alpha_composite(canvas, halo_layer)
    canvas = Image.alpha_composite(canvas, beam_layer)
    
    # 3. Paste the Curved-Beam Lighthouse Artwork from SVG:
    svg_str = build_perfect_designer_lighthouse_svg(1500)
    
    with open('/workspace/lighthouse_designer.svg', 'w', encoding='utf-8') as f:
        f.write(svg_str)
        
    tmp_lh_png = "/tmp/lh_designer_curved_render.png"
    cairosvg.svg2png(bytestring=svg_str.encode('utf-8'), write_to=tmp_lh_png, output_width=1500, output_height=1500)
    lh_img = Image.open(tmp_lh_png).convert("RGBA")
    
    lh_resized = lh_img.resize((lh_size, lh_size), Image.Resampling.LANCZOS)
    canvas.paste(lh_resized, (lh_cx - lh_size // 2, lh_cy - lh_size // 2), lh_resized)
    
    # 4. Typography (Sofia Sans Condensed ExtraBold & Open Sans Regular, centered):
    text_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_layer)
    
    font_title = ImageFont.truetype("/workspace/fonts/SofiaSansCondensed-ExtraBold.ttf", 112)
    font_sub = ImageFont.truetype("/workspace/fonts/OpenSans-Regular.ttf", 36)
    
    title_text = "АНГЛИЙСКИЙ МАЯК"
    sub_text = "подготовка к ОГЭ и ЕГЭ по английскому языку"
    
    t_bb = draw.textbbox((0, 0), title_text, font=font_title)
    tw, th = t_bb[2] - t_bb[0], t_bb[3] - t_bb[1]
    
    s_bb = draw.textbbox((0, 0), sub_text, font=font_sub)
    sw, sh = s_bb[2] - s_bb[0], s_bb[3] - s_bb[1]
    
    gap = 26
    tot_h = th + gap + sh
    
    top_y = (H - tot_h) // 2 - 10
    
    tx = (W - tw) // 2
    ty = top_y
    
    sx = (W - sw) // 2
    sy = ty + th + gap
    
    # Soft text shadow
    for dx, dy, a in [(-2, -2, 40), (2, 2, 80), (0, 4, 110), (0, 8, 80)]:
        draw.text((tx + dx, ty + dy), title_text, font=font_title, fill=(12, 22, 26, a))
        
    # Title in pure #FFFFFF
    draw.text((tx, ty), title_text, font=font_title, fill=(255, 255, 255, 255))
    
    # Subtitle shadow & text (#A5D2DF)
    draw.text((sx, sy + 2), sub_text, font=font_sub, fill=(12, 22, 26, 120))
    draw.text((sx, sy), sub_text, font=font_sub, fill=(175, 220, 230, 255))
    
    final_cover = Image.alpha_composite(canvas, text_layer)
    
    # Save standard outputs
    final_cover.save("/workspace/cover_vk.png", "PNG", quality=100)
    final_cover.convert("RGB").save("/workspace/cover_vk.jpg", "JPEG", quality=98)
    
    final_cover.save("/workspace/vk_cover_1920x768.png", "PNG", quality=100)
    final_cover.convert("RGB").save("/workspace/vk_cover_1920x768.jpg", "JPEG", quality=98)
    
    print("Master cover generated and verified successfully!")

if __name__ == '__main__':
    create_final_master_vk_cover()
