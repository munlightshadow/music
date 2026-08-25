import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cairosvg

def create_pure_original_lighthouse_svg():
    """
    Exact vector SVG of the lighthouse matching the attached image:
    - Pure white lighthouse tower (#FFFFFF) with dark navy windows/doors (#214149)
    - Gold expanding light beams (#F3D593 -> #C19B4F)
    - Pure white rocky island (#FFFFFF) with dark contour lines (#214149)
    - Water ripples below (#A5D2DF and #FFFFFF)
    - No external circle border
    """
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="1000" height="1000">
  <defs>
    <linearGradient id="goldBeamL" x1="470" y1="385" x2="50" y2="395" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#F3D593" stop-opacity="0.95" />
      <stop offset="40%" stop-color="#C19B4F" stop-opacity="0.80" />
      <stop offset="100%" stop-color="#C19B4F" stop-opacity="0.65" />
    </linearGradient>

    <linearGradient id="goldBeamR" x1="530" y1="385" x2="950" y2="395" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#F3D593" stop-opacity="0.95" />
      <stop offset="40%" stop-color="#C19B4F" stop-opacity="0.80" />
      <stop offset="100%" stop-color="#C19B4F" stop-opacity="0.65" />
    </linearGradient>

    <radialGradient id="lanternCore" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#FFFFFF" />
      <stop offset="30%" stop-color="#FFF2CE" />
      <stop offset="70%" stop-color="#F3D593" />
      <stop offset="100%" stop-color="#C19B4F" />
    </radialGradient>
  </defs>

  <g id="lighthouse_pure">
    <!-- Golden Light Beams (expanding trapezoids) -->
    <polygon points="465,372 40,366 40,422 465,398" fill="url(#goldBeamL)" />
    <polygon points="535,372 960,366 960,422 535,398" fill="url(#goldBeamR)" />

    <!-- Water Ripples -->
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

    <!-- Rocky Island Silhouette (Solid Pure White) -->
    <path d="M 310 684
             C 330 670, 360 662, 390 660
             C 410 650, 425 642, 442 638
             L 558 638
             C 575 642, 590 650, 610 660
             C 640 662, 670 670, 690 684
             C 610 692, 390 692, 310 684 Z"
          fill="#FFFFFF" />

    <!-- Rock Inner Crevice / Shadow Lines (#214149) -->
    <path d="M 345 676 C 395 666, 450 672, 500 670 C 550 672, 605 666, 655 676" stroke="#214149" stroke-width="4.5" fill="none" stroke-linecap="round"/>
    <path d="M 390 663 C 430 654, 470 656, 500 654 C 530 656, 570 654, 610 663" stroke="#214149" stroke-width="3.5" fill="none" stroke-linecap="round"/>
    <path d="M 435 648 C 465 643, 500 644, 535 643 C 548 645, 558 647, 565 650" stroke="#214149" stroke-width="3" fill="none" stroke-linecap="round"/>

    <!-- Lighthouse Tower Body (Solid Pure White) -->
    <polygon points="445,638 464,426 536,426 555,638" fill="#FFFFFF" />

    <!-- Vertical Accent Line on Tower -->
    <path d="M 500,426 L 536,426 L 555,638 L 500,638 Z" fill="#214149" opacity="0.04" />

    <!-- Tower Windows & Doors (Dark #214149) -->
    <path d="M 488 618 L 488 584 C 488 576, 512 576, 512 584 L 512 618 Z" fill="#214149" />
    <rect x="489" y="500" width="22" height="34" rx="11" fill="#214149" />
    <rect x="490" y="442" width="20" height="28" rx="10" fill="#214149" />

    <!-- Gallery Platform -->
    <rect x="448" y="420" width="104" height="8" rx="2" fill="#FFFFFF" />
    <line x1="448" y1="428" x2="552" y2="428" stroke="#214149" stroke-width="2" opacity="0.3"/>

    <!-- Balcony Railing -->
    <line x1="450" y1="407" x2="550" y2="407" stroke="#FFFFFF" stroke-width="3.5" stroke-linecap="round"/>
    <line x1="452" y1="414" x2="548" y2="414" stroke="#FFFFFF" stroke-width="2" />
    <line x1="454" y1="407" x2="454" y2="420" stroke="#FFFFFF" stroke-width="3" />
    <line x1="472" y1="407" x2="472" y2="420" stroke="#FFFFFF" stroke-width="2.5" />
    <line x1="490" y1="407" x2="490" y2="420" stroke="#FFFFFF" stroke-width="2.5" />
    <line x1="510" y1="407" x2="510" y2="420" stroke="#FFFFFF" stroke-width="2.5" />
    <line x1="528" y1="407" x2="528" y2="420" stroke="#FFFFFF" stroke-width="2.5" />
    <line x1="546" y1="407" x2="546" y2="420" stroke="#FFFFFF" stroke-width="3" />

    <!-- Lantern Room Structure -->
    <rect x="464" y="366" width="72" height="42" fill="#FFFFFF" />
    <rect x="470" y="370" width="60" height="34" rx="2" fill="#214149" />
    
    <!-- Glowing Central Lantern Bulb -->
    <circle cx="500" cy="387" r="10" fill="url(#lanternCore)" />
    <rect x="496" y="370" width="8" height="34" fill="#F3D593" opacity="0.95"/>
    
    <!-- Lantern Panes -->
    <line x1="484" y1="370" x2="484" y2="404" stroke="#FFFFFF" stroke-width="2.5" />
    <line x1="516" y1="370" x2="516" y2="404" stroke="#FFFFFF" stroke-width="2.5" />

    <!-- Lantern Cornice Platform -->
    <rect x="460" y="362" width="80" height="6" rx="2" fill="#FFFFFF" />

    <!-- Lantern Dome / Cupola -->
    <path d="M 464 362 
             C 464 336, 480 332, 500 332 
             C 520 332, 536 336, 536 362 Z" 
          fill="#FFFFFF" />

    <!-- Dome Spire & Finial -->
    <rect x="495" y="322" width="10" height="11" rx="2" fill="#FFFFFF" />
    <circle cx="500" cy="316" r="7" fill="#FFFFFF" />
    <line x1="500" y1="298" x2="500" y2="312" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round"/>
  </g>
</svg>'''
    return svg

def create_exact_user_cover():
    # Target size: 1920x768 (standard VK cover resolution)
    # The source full image is 1920x1080 (the exact image user sent in the message)
    # When cropped to 1920x768 in the VK editor (lower selection box), it cuts the top ~312px.
    
    FULL_W, FULL_H = 1920, 1080
    TARGET_W, TARGET_H = 1920, 768
    
    # 1. Background Sea Gradient of the 1920x1080 canvas:
    # Matches the uncropped image user sent:
    # Smooth diagonal gradient from top-left to bottom-right:
    # Top-left: #20424D
    # Bottom-right: #45889B
    y_coords, x_coords = np.mgrid[0:FULL_H, 0:FULL_W]
    t = 0.70 * (y_coords / FULL_H) + 0.30 * (x_coords / FULL_W)
    t = np.clip(t, 0.0, 1.0)
    
    c_top = np.array([33, 65, 73], dtype=np.float32)       # #214149
    c_bot = np.array([72, 141, 160], dtype=np.float32)     # #488DA0
    
    rgb = (1.0 - t[:, :, np.newaxis]) * c_top + t[:, :, np.newaxis] * c_bot
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    full_bg = Image.fromarray(rgb, "RGB").convert("RGBA")
    
    # 2. Lighting / Halo around the lighthouse in the 1080p canvas:
    # In the 1080p image:
    # Lighthouse center: x = 1650, y = 800
    # Lantern y: ~750
    lh_cx = 1650
    lh_cy = 800
    lh_size = 500
    
    lantern_x = lh_cx
    lantern_y = lh_cy - int(lh_size * 0.12)
    
    halo_layer = Image.new("RGBA", (FULL_W, FULL_H), (0, 0, 0, 0))
    hdraw = ImageDraw.Draw(halo_layer)
    hdraw.ellipse((lantern_x - 220, lantern_y - 170, lantern_x + 220, lantern_y + 170), fill=(193, 155, 79, 36))
    hdraw.ellipse((lantern_x - 140, lantern_y - 110, lantern_x + 140, lantern_y + 110), fill=(243, 213, 147, 42))
    halo_layer = halo_layer.filter(ImageFilter.GaussianBlur(45))
    
    # Light beam sweeping gently
    beam_layer = Image.new("RGBA", (FULL_W, FULL_H), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(beam_layer)
    bdraw.polygon([(lantern_x - 20, lantern_y - 10), (0, 350), (0, 680), (lantern_x - 20, lantern_y + 15)], fill=(243, 213, 147, 18))
    bdraw.polygon([(lantern_x + 20, lantern_y - 10), (FULL_W, 600), (FULL_W, 850), (lantern_x + 20, lantern_y + 15)], fill=(243, 213, 147, 18))
    beam_layer = beam_layer.filter(ImageFilter.GaussianBlur(30))
    
    full_canvas = Image.alpha_composite(full_bg, halo_layer)
    full_canvas = Image.alpha_composite(full_canvas, beam_layer)
    
    # 3. Paste the Pure Lighthouse Artwork (from SVG):
    lh_svg = create_pure_original_lighthouse_svg()
    tmp_lh_path = "/tmp/lh_pure_orig.png"
    cairosvg.svg2png(bytestring=lh_svg.encode('utf-8'), write_to=tmp_lh_path, output_width=1500, output_height=1500)
    lh_img = Image.open(tmp_lh_path).convert("RGBA")
    
    lh_resized = lh_img.resize((lh_size, lh_size), Image.Resampling.LANCZOS)
    full_canvas.paste(lh_resized, (lh_cx - lh_size // 2, lh_cy - lh_size // 2), lh_resized)
    
    # Save the full 1080p image (matching the exact image user provided)
    full_canvas.save("/workspace/vk_full_1080p.png", "PNG")
    full_canvas.convert("RGB").save("/workspace/vk_full_1080p.jpg", "JPEG", quality=98)
    
    # 4. Crop to VK Cover (1920x768):
    # In VK Editor: the selection box is aligned with the bottom of the 1080p image
    # Crop bounds: (0, 1080 - 768 = 312, 1920, 1080)
    crop_top = FULL_H - TARGET_H # 312
    cover_1920x768 = full_canvas.crop((0, crop_top, TARGET_W, FULL_H))
    
    # 5. Add Typography strictly as required:
    # "Посередине прямоугольника крупная надпись. Название «Английский маяк» стоит ровно по центру над второй строчкой: «подготовка к ОГЭ и ЕГЭ по английскому языку»."
    # "Шрифты:
    # Название — Sofia Sans Condensed ExtraBold
    # Вторая строка — Open Sans Regular"
    
    text_layer = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
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
    
    top_y = (TARGET_H - tot_h) // 2 - 10
    
    tx = (TARGET_W - tw) // 2
    ty = top_y
    
    sx = (TARGET_W - sw) // 2
    sy = ty + th + gap
    
    # Soft text shadows for maximum readability and aesthetics
    for dx, dy, a in [(-2, -2, 40), (2, 2, 80), (0, 4, 110), (0, 8, 80)]:
        draw.text((tx + dx, ty + dy), title_text, font=font_title, fill=(12, 22, 26, a))
        
    # Title in pure #FFFFFF
    draw.text((tx, ty), title_text, font=font_title, fill=(255, 255, 255, 255))
    
    # Subtitle shadow & text (#A5D2DF / light sea aqua)
    draw.text((sx, sy + 2), sub_text, font=font_sub, fill=(12, 22, 26, 120))
    draw.text((sx, sy), sub_text, font=font_sub, fill=(175, 220, 230, 255))
    
    final_cover = Image.alpha_composite(cover_1920x768, text_layer)
    
    # Save standard outputs in 1920x768
    final_cover.save("/workspace/cover_vk.png", "PNG", quality=100)
    final_cover.convert("RGB").save("/workspace/cover_vk.jpg", "JPEG", quality=98)
    
    final_cover.save("/workspace/vk_cover_1920x768.png", "PNG", quality=100)
    final_cover.convert("RGB").save("/workspace/vk_cover_1920x768.jpg", "JPEG", quality=98)

    print("All cover files generated successfully!")

if __name__ == '__main__':
    create_exact_user_cover()
