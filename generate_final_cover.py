import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cairosvg

def create_perfect_vk_cover(
    output_png="/workspace/cover_vk.png",
    output_jpg="/workspace/cover_vk.jpg"
):
    W, H = 1920, 768
    
    # 1. Background Sea Gradient:
    # Deep sea navy/teal at the top, soft rich sea teal with gentle lighting towards bottom
    y_coords, x_coords = np.mgrid[0:H, 0:W]
    
    c_top = np.array([23, 39, 45], dtype=np.float32)
    c_mid = np.array([38, 72, 82], dtype=np.float32)
    c_bottom = np.array([56, 110, 124], dtype=np.float32)
    
    norm_y = y_coords / H
    norm_x = x_coords / W
    
    t1 = np.clip(norm_y * 1.35 - 0.1, 0.0, 1.0)
    rgb_base = (1.0 - t1[:, :, np.newaxis]) * c_top + t1[:, :, np.newaxis] * c_mid
    
    t2 = np.clip((norm_y - 0.35) / 0.65, 0.0, 1.0)
    rgb_base = (1.0 - t2[:, :, np.newaxis] * 0.55) * rgb_base + (t2[:, :, np.newaxis] * 0.55) * c_bottom
    
    rgb_base = np.clip(rgb_base, 0, 255).astype(np.uint8)
    bg_img = Image.fromarray(rgb_base, "RGB").convert("RGBA")
    
    # 2. Soft Atmospheric Fog & Blurred Sea Waves (Mist)
    mist_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    mist_draw = ImageDraw.Draw(mist_layer)
    
    mist_draw.ellipse((-300, 320, 1100, 950), fill=(72, 141, 160, 45))
    mist_draw.ellipse((500, 380, 1900, 1050), fill=(70, 138, 157, 55))
    mist_draw.ellipse((1100, 260, 2200, 950), fill=(72, 141, 160, 50))
    mist_layer = mist_layer.filter(ImageFilter.GaussianBlur(90))
    
    # 3. Lighthouse Position & Sizing
    # Matches the VK Editor crop layout perfectly
    lh_cx = 1640
    lh_cy = 560
    lh_size = 520
    
    lantern_x = lh_cx
    lantern_y = lh_cy - int(lh_size * 0.12)
    
    # Warm radial halo behind the lantern
    halo_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hdraw = ImageDraw.Draw(halo_layer)
    hdraw.ellipse((lantern_x - 260, lantern_y - 200, lantern_x + 260, lantern_y + 200), fill=(193, 155, 79, 45))
    hdraw.ellipse((lantern_x - 170, lantern_y - 130, lantern_x + 170, lantern_y + 130), fill=(243, 213, 147, 50))
    hdraw.ellipse((lantern_x - 90, lantern_y - 70, lantern_x + 90, lantern_y + 70), fill=(255, 248, 220, 60))
    halo_layer = halo_layer.filter(ImageFilter.GaussianBlur(45))
    
    # Composite background layers
    canvas = Image.alpha_composite(bg_img, mist_layer)
    canvas = Image.alpha_composite(canvas, halo_layer)
    
    # 4. Render Updated Vector Lighthouse Artwork from SVG
    from generate_accurate_lh import generate_perfect_logo_lighthouse_svg
    svg_str = generate_perfect_logo_lighthouse_svg(1500)
    tmp_lh_png = "/tmp/lh_transparent_rendered.png"
    cairosvg.svg2png(bytestring=svg_str.encode('utf-8'), write_to=tmp_lh_png, output_width=1500, output_height=1500)
    lh_img = Image.open(tmp_lh_png).convert("RGBA")
    
    lh_resized = lh_img.resize((lh_size, lh_size), Image.Resampling.LANCZOS)
    canvas.paste(lh_resized, (lh_cx - lh_size // 2, lh_cy - lh_size // 2), lh_resized)
    
    # 5. Centered Typography (Unchanged)
    # Title: «АНГЛИЙСКИЙ МАЯК» — Sofia Sans Condensed ExtraBold (800)
    # Subtitle: «подготовка к ОГЭ и ЕГЭ по английскому языку» — Open Sans Regular (400)
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
    
    # Text shadow for title
    for dx, dy, a in [(-2, -2, 40), (2, 2, 80), (0, 4, 110), (0, 8, 80)]:
        draw.text((tx + dx, ty + dy), title_text, font=font_title, fill=(12, 22, 26, a))
        
    # Title text (#FFFFFF)
    draw.text((tx, ty), title_text, font=font_title, fill=(255, 255, 255, 255))
    
    # Subtitle shadow & text (#A5D2DF)
    draw.text((sx, sy + 2), sub_text, font=font_sub, fill=(12, 22, 26, 120))
    draw.text((sx, sy), sub_text, font=font_sub, fill=(175, 220, 230, 255))
    
    # Composite final image
    final_cover = Image.alpha_composite(canvas, text_layer)
    
    # Save standard outputs
    final_cover.save(output_png, "PNG", quality=100)
    final_cover.convert("RGB").save(output_jpg, "JPEG", quality=98)
    
    final_cover.save("/workspace/vk_cover_1920x768.png", "PNG", quality=100)
    final_cover.convert("RGB").save("/workspace/vk_cover_1920x768.jpg", "JPEG", quality=98)
    
    print(f"Generated {output_png} and {output_jpg} (1920x768) successfully!")

if __name__ == '__main__':
    create_perfect_vk_cover()
