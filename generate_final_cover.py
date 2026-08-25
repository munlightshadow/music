import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cairosvg

def create_master_cover_designer_artwork():
    W, H = 1920, 768
    
    # 1. Background Sea Gradient:
    # Deep, smooth, clean sea gradient (#1A333A at top to #488DA0 at bottom)
    y_coords, x_coords = np.mgrid[0:H, 0:W]
    
    c_top = np.array([26, 51, 58], dtype=np.float32)       # #1A333A
    c_mid = np.array([33, 65, 73], dtype=np.float32)       # #214149
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
    
    # Lighthouse position in bottom right (matches layout):
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
    
    # 3. Paste the True Designer Lighthouse Artwork from SVG:
    from test_designer_svg_v3 import build_designer_exact_svg_v3
    svg_str = build_designer_exact_svg_v3(1500)
    
    # Also save the official SVG file in the repo
    with open('/workspace/lighthouse_designer.svg', 'w', encoding='utf-8') as f:
        f.write(svg_str)
        
    tmp_lh_png = "/tmp/lh_designer_render.png"
    cairosvg.svg2png(bytestring=svg_str.encode('utf-8'), write_to=tmp_lh_png, output_width=1500, output_height=1500)
    lh_img = Image.open(tmp_lh_png).convert("RGBA")
    
    lh_resized = lh_img.resize((lh_size, lh_size), Image.Resampling.LANCZOS)
    canvas.paste(lh_resized, (lh_cx - lh_size // 2, lh_cy - lh_size // 2), lh_resized)
    
    # 4. Typography (Exact fonts, sizes, colors and central placement):
    # Title: «АНГЛИЙСКИЙ МАЯК» — Sofia Sans Condensed ExtraBold (800), #FFFFFF
    # Subtitle: «подготовка к ОГЭ и ЕГЭ по английскому языку» — Open Sans Regular (400), #A5D2DF
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
    
    print("Master cover generated successfully!")

if __name__ == '__main__':
    create_master_cover_designer_artwork()
