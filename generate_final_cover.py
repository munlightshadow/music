import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cairosvg

def create_final_vk_cover():
    W, H = 1920, 768
    
    # Generate SVG of the emblem
    from generate_exact_lighthouse import generate_exact_lighthouse_svg
    svg_str = generate_exact_lighthouse_svg(1500)
    
    tmp_emblem_path = "/tmp/lighthouse_final_emblem.png"
    cairosvg.svg2png(bytestring=svg_str.encode('utf-8'), write_to=tmp_emblem_path, output_width=1500, output_height=1500)
    emblem_img = Image.open(tmp_emblem_path).convert("RGBA")
    
    # 1. Background Sea Gradient: море #488DA0 -> #1A333A
    # Palette colors:
    # #488DA0 (72, 141, 160)
    # #1A333A (26, 51, 58)
    y_coords, x_coords = np.mgrid[0:H, 0:W]
    t = 0.70 * (y_coords / H) + 0.30 * (x_coords / W)
    t = np.clip(t, 0.0, 1.0)
    
    c_top = np.array([72, 141, 160], dtype=np.float32)
    c_bot = np.array([26, 51, 58], dtype=np.float32)
    
    rgb = (1.0 - t[:, :, np.newaxis]) * c_top + t[:, :, np.newaxis] * c_bot
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    bg_img = Image.fromarray(rgb, "RGB").convert("RGBA")
    
    # 2. Lighting & Emblem Placement in bottom right
    # For a 1920x768 cover, let's position the emblem nicely in the right area
    # Center: x = 1630, y = 560, diameter = 560 (radius 280)
    # Bottom reaches 560 + 280 = 840 (clipped at 768), right reaches 1630 + 280 = 1910
    # This gives a modern crop/bleed in the corner
    lh_cx, lh_cy = 1630, 560
    emblem_diam = 560
    
    # Ambient Light sweeping to the left
    light_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ldraw = ImageDraw.Draw(light_layer)
    ldraw.polygon(
        [(lh_cx - 30, lh_cy - 85), (0, 110), (0, 390), (lh_cx - 30, lh_cy - 45)],
        fill=(243, 213, 147, 24)
    )
    ldraw.polygon(
        [(lh_cx - 30, lh_cy - 75), (0, 170), (0, 310), (lh_cx - 30, lh_cy - 55)],
        fill=(255, 255, 255, 16)
    )
    light_layer = light_layer.filter(ImageFilter.GaussianBlur(22))
    
    # Drop shadow & subtle golden glow behind emblem
    shadow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow_layer)
    sdraw.ellipse(
        (lh_cx - emblem_diam//2 - 14, lh_cy - emblem_diam//2 - 14,
         lh_cx + emblem_diam//2 + 14, lh_cy + emblem_diam//2 + 14),
        fill=(10, 20, 25, 140)
    )
    sdraw.ellipse(
        (lh_cx - emblem_diam//2 - 6, lh_cy - emblem_diam//2 - 6,
         lh_cx + emblem_diam//2 + 6, lh_cy + emblem_diam//2 + 6),
        fill=(193, 155, 79, 40)
    )
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(22))
    
    canvas = Image.alpha_composite(bg_img, light_layer)
    canvas = Image.alpha_composite(canvas, shadow_layer)
    
    emblem_resized = emblem_img.resize((emblem_diam, emblem_diam), Image.Resampling.LANCZOS)
    canvas.paste(emblem_resized, (lh_cx - emblem_diam // 2, lh_cy - emblem_diam // 2), emblem_resized)
    
    # 3. Typography
    # Title: «АНГЛИЙСКИЙ МАЯК» in Sofia Sans Condensed ExtraBold
    # Subtitle: «подготовка к ОГЭ и ЕГЭ по английскому языку» in Open Sans Regular
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
    top_y = (H - tot_h) // 2 - 12
    
    tx = (W - tw) // 2
    ty = top_y
    
    sx = (W - sw) // 2
    sy = ty + th + gap
    
    # Soft text shadow
    for dx, dy, a in [(-2, -2, 40), (2, 2, 80), (0, 4, 110), (0, 8, 80)]:
        draw.text((tx + dx, ty + dy), title_text, font=font_title, fill=(12, 25, 30, a))
        
    # Title (#FFFFFF)
    draw.text((tx, ty), title_text, font=font_title, fill=(255, 255, 255, 255))
    
    # Subtitle shadow & text (#A5D2DF / light sea blue)
    draw.text((sx, sy + 2), sub_text, font=font_sub, fill=(12, 25, 30, 120))
    draw.text((sx, sy), sub_text, font=font_sub, fill=(175, 222, 233, 255))
    
    # Composite final image
    final_cover = Image.alpha_composite(canvas, text_layer)
    
    # Save standard files
    final_cover.save("/workspace/cover_vk.png", "PNG", quality=100)
    final_cover.convert("RGB").save("/workspace/cover_vk.jpg", "JPEG", quality=98)
    
    final_cover.save("/workspace/vk_cover_1920x768.png", "PNG", quality=100)
    final_cover.convert("RGB").save("/workspace/vk_cover_1920x768.jpg", "JPEG", quality=98)

    print("All cover files generated successfully!")

if __name__ == '__main__':
    create_final_vk_cover()
