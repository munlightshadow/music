import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cairosvg

def build_white_lighthouse_svg(size=2000):
    """
    Variant 2 Lighthouse:
    Solid white lighthouse structure (as seen in the original color logo badge on blue sea):
    - Pure white dome, spire, railing, tower body, and rock base.
    - Dark navy windows/door (#214149).
    - Gold expanding light beams with circular arc outer edges (#F3D593 -> #C19B4F).
    - Water ripples under rock (white #FFFFFF and aqua #A5D2DF).
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

  <g id="white_lighthouse_artwork">
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

    <!-- 2. Water Reflection Wave Lines (White and Aqua) -->
    <g stroke-linecap="round">
      <line x1="180" y1="676" x2="820" y2="676" stroke="#A5D2DF" stroke-width="4.5" opacity="0.75" />
      <line x1="120" y1="692" x2="880" y2="692" stroke="#FFFFFF" stroke-width="5.5" opacity="0.95" />
      <line x1="160" y1="708" x2="840" y2="708" stroke="#A5D2DF" stroke-width="6" opacity="0.85" />
      <line x1="210" y1="724" x2="790" y2="724" stroke="#FFFFFF" stroke-width="5.5" opacity="0.95" />
      <line x1="265" y1="740" x2="735" y2="740" stroke="#A5D2DF" stroke-width="5.5" opacity="0.85" />
      <line x1="320" y1="756" x2="680" y2="756" stroke="#FFFFFF" stroke-width="5" opacity="0.9" />
      <line x1="380" y1="772" x2="620" y2="772" stroke="#A5D2DF" stroke-width="4.5" opacity="0.8" />
      <line x1="435" y1="788" x2="565" y2="788" stroke="#FFFFFF" stroke-width="4" opacity="0.85" />
      <line x1="465" y1="804" x2="535" y2="804" stroke="#A5D2DF" stroke-width="3.5" opacity="0.7" />
      <line x1="485" y1="820" x2="515" y2="820" stroke="#FFFFFF" stroke-width="3" opacity="0.6" />
    </g>

    <!-- 3. Rocky Island Base (Solid Pure White with dark contours) -->
    <path d="M 310 684
             C 330 670, 360 662, 390 660
             C 410 650, 425 642, 442 638
             L 558 638
             C 575 642, 590 650, 610 660
             C 640 662, 670 670, 690 684
             C 610 692, 390 692, 310 684 Z"
          fill="#FFFFFF" />

    <!-- Rock Inner Crevice Lines (#214149) -->
    <path d="M 345 676 C 395 666, 450 672, 500 670 C 550 672, 605 666, 655 676" stroke="#214149" stroke-width="4.5" fill="none" stroke-linecap="round"/>
    <path d="M 390 663 C 430 654, 470 656, 500 654 C 530 656, 570 654, 610 663" stroke="#214149" stroke-width="3.5" fill="none" stroke-linecap="round"/>
    <path d="M 435 648 C 465 643, 500 644, 535 643 C 548 645, 558 647, 565 650" stroke="#214149" stroke-width="3" fill="none" stroke-linecap="round"/>

    <!-- 4. Lighthouse Tower Body (Solid Pure White) -->
    <polygon points="445,638 464,426 536,426 555,638" fill="#FFFFFF" />

    <!-- Tower Windows & Doors (Dark Navy #214149) -->
    <!-- Base Entryway Door -->
    <path d="M 488 618 L 488 584 C 488 576, 512 576, 512 584 L 512 618 Z" fill="#214149" />
    
    <!-- Middle Arched Window -->
    <rect x="489" y="500" width="22" height="34" rx="11" fill="#214149" />

    <!-- Upper Arched Window -->
    <rect x="490" y="442" width="20" height="28" rx="10" fill="#214149" />

    <!-- 5. Balcony / Gallery Platform (Solid Pure White) -->
    <rect x="448" y="420" width="104" height="8" rx="2" fill="#FFFFFF" />
    <line x1="448" y1="428" x2="552" y2="428" stroke="#214149" stroke-width="2" opacity="0.3"/>

    <!-- Balcony Railing (White) -->
    <line x1="450" y1="407" x2="550" y2="407" stroke="#FFFFFF" stroke-width="3.5" stroke-linecap="round"/>
    <!-- Railing Posts -->
    <line x1="454" y1="407" x2="454" y2="420" stroke="#FFFFFF" stroke-width="3" />
    <line x1="472" y1="407" x2="472" y2="420" stroke="#FFFFFF" stroke-width="2.5" />
    <line x1="490" y1="407" x2="490" y2="420" stroke="#FFFFFF" stroke-width="2.5" />
    <line x1="510" y1="407" x2="510" y2="420" stroke="#FFFFFF" stroke-width="2.5" />
    <line x1="528" y1="407" x2="528" y2="420" stroke="#FFFFFF" stroke-width="2.5" />
    <line x1="546" y1="407" x2="546" y2="420" stroke="#FFFFFF" stroke-width="3" />

    <!-- 6. Lantern Chamber (White structure with dark glass room & central lamp) -->
    <rect x="464" y="366" width="72" height="42" fill="#FFFFFF" />
    <rect x="470" y="370" width="60" height="34" rx="2" fill="#214149" />
    
    <!-- Central Glowing Lantern Bulb -->
    <circle cx="500" cy="387" r="10" fill="url(#lampGlow)" />
    <rect x="496" y="370" width="8" height="34" fill="#F3D593" opacity="0.95"/>
    
    <!-- Vertical Frame Mullions -->
    <line x1="484" y1="370" x2="484" y2="404" stroke="#FFFFFF" stroke-width="2.5" />
    <line x1="516" y1="370" x2="516" y2="404" stroke="#FFFFFF" stroke-width="2.5" />

    <!-- Lantern Cornice Platform -->
    <rect x="460" y="362" width="80" height="6" rx="2" fill="#FFFFFF" />

    <!-- 7. Lantern Dome / Cupola (Solid Pure White) -->
    <path d="M 464 362 
             C 464 336, 480 332, 500 332 
             C 520 332, 536 336, 536 362 Z" 
          fill="#FFFFFF" />

    <!-- 8. Spire & Finial (White) -->
    <rect x="495" y="322" width="10" height="11" rx="2" fill="#FFFFFF" />
    <circle cx="500" cy="316" r="7" fill="#FFFFFF" />
    <line x1="500" y1="298" x2="500" y2="312" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round"/>
  </g>
</svg>'''
    return svg

def render_both_variants():
    W, H = 1920, 768
    
    # 1. Common Background Sea Gradient:
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
    
    # 2. Common Atmospheric Mist & Glow:
    mist_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    mist_draw = ImageDraw.Draw(mist_layer)
    mist_draw.ellipse((-200, 250, 1100, 900), fill=(72, 141, 160, 45))
    mist_draw.ellipse((500, 320, 1900, 1000), fill=(70, 138, 157, 50))
    mist_draw.ellipse((1100, 200, 2200, 900), fill=(72, 141, 160, 45))
    mist_layer = mist_layer.filter(ImageFilter.GaussianBlur(90))
    
    lh_cx = 1640
    lh_cy = 575
    lh_size = 460
    
    lantern_x = lh_cx
    lantern_y = lh_cy - int(lh_size * 0.14)
    
    halo_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hdraw = ImageDraw.Draw(halo_layer)
    hdraw.ellipse((lantern_x - 240, lantern_y - 180, lantern_x + 240, lantern_y + 180), fill=(193, 155, 79, 40))
    hdraw.ellipse((lantern_x - 150, lantern_y - 110, lantern_x + 150, lantern_y + 110), fill=(243, 213, 147, 45))
    hdraw.ellipse((lantern_x - 80, lantern_y - 60, lantern_x + 80, lantern_y + 60), fill=(255, 248, 220, 55))
    halo_layer = halo_layer.filter(ImageFilter.GaussianBlur(40))
    
    beam_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(beam_layer)
    bdraw.polygon([(lantern_x - 20, lantern_y - 10), (0, 320), (0, 580), (lantern_x - 20, lantern_y + 15)], fill=(243, 213, 147, 18))
    bdraw.polygon([(lantern_x + 20, lantern_y - 10), (W, 480), (W, 640), (lantern_x + 20, lantern_y + 15)], fill=(243, 213, 147, 18))
    beam_layer = beam_layer.filter(ImageFilter.GaussianBlur(30))
    
    canvas_base = Image.alpha_composite(bg_img, mist_layer)
    canvas_base = Image.alpha_composite(canvas_base, halo_layer)
    canvas_base = Image.alpha_composite(canvas_base, beam_layer)
    
    # 3. Typography:
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
    
    for dx, dy, a in [(-2, -2, 40), (2, 2, 80), (0, 4, 110), (0, 8, 80)]:
        draw.text((tx + dx, ty + dy), title_text, font=font_title, fill=(12, 22, 26, a))
        
    draw.text((tx, ty), title_text, font=font_title, fill=(255, 255, 255, 255))
    draw.text((sx, sy + 2), sub_text, font=font_sub, fill=(12, 22, 26, 120))
    draw.text((sx, sy), sub_text, font=font_sub, fill=(175, 220, 230, 255))
    
    # --- VARIANT 1: Two-Tone Colored Designer Lighthouse ---
    from generate_final_cover import build_perfect_designer_lighthouse_svg
    svg_v1 = build_perfect_designer_lighthouse_svg(1500)
    with open('/workspace/lighthouse_variant1.svg', 'w', encoding='utf-8') as f:
        f.write(svg_v1)
    cairosvg.svg2png(bytestring=svg_v1.encode('utf-8'), write_to="/tmp/lh_v1.png", output_width=1500, output_height=1500)
    lh_v1_img = Image.open("/tmp/lh_v1.png").convert("RGBA").resize((lh_size, lh_size), Image.Resampling.LANCZOS)
    
    canvas_v1 = canvas_base.copy()
    canvas_v1.paste(lh_v1_img, (lh_cx - lh_size // 2, lh_cy - lh_size // 2), lh_v1_img)
    final_v1 = Image.alpha_composite(canvas_v1, text_layer)
    
    final_v1.save("/workspace/cover_vk_variant1.png", "PNG", quality=100)
    final_v1.convert("RGB").save("/workspace/cover_vk_variant1.jpg", "JPEG", quality=98)
    final_v1.save("/workspace/vk_cover_variant1.png", "PNG", quality=100)
    final_v1.convert("RGB").save("/workspace/vk_cover_variant1.jpg", "JPEG", quality=98)
    print("Saved Variant 1 files!")
    
    # --- VARIANT 2: White Lighthouse (from original color emblem on blue sea) ---
    svg_v2 = build_white_lighthouse_svg(1500)
    with open('/workspace/lighthouse_variant2.svg', 'w', encoding='utf-8') as f:
        f.write(svg_v2)
    with open('/workspace/lighthouse_designer.svg', 'w', encoding='utf-8') as f:
        f.write(svg_v2)
        
    cairosvg.svg2png(bytestring=svg_v2.encode('utf-8'), write_to="/tmp/lh_v2.png", output_width=1500, output_height=1500)
    lh_v2_img = Image.open("/tmp/lh_v2.png").convert("RGBA").resize((lh_size, lh_size), Image.Resampling.LANCZOS)
    
    canvas_v2 = canvas_base.copy()
    canvas_v2.paste(lh_v2_img, (lh_cx - lh_size // 2, lh_cy - lh_size // 2), lh_v2_img)
    final_v2 = Image.alpha_composite(canvas_v2, text_layer)
    
    final_v2.save("/workspace/cover_vk_variant2.png", "PNG", quality=100)
    final_v2.convert("RGB").save("/workspace/cover_vk_variant2.jpg", "JPEG", quality=98)
    final_v2.save("/workspace/vk_cover_variant2.png", "PNG", quality=100)
    final_v2.convert("RGB").save("/workspace/vk_cover_variant2.jpg", "JPEG", quality=98)
    
    # Also update the primary files cover_vk.png / jpg to Variant 2
    final_v2.save("/workspace/cover_vk.png", "PNG", quality=100)
    final_v2.convert("RGB").save("/workspace/cover_vk.jpg", "JPEG", quality=98)
    final_v2.save("/workspace/vk_cover_1920x768.png", "PNG", quality=100)
    final_v2.convert("RGB").save("/workspace/vk_cover_1920x768.jpg", "JPEG", quality=98)
    print("Saved Variant 2 files!")

if __name__ == '__main__':
    render_both_variants()
