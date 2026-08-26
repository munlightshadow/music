import os
import cairosvg

def generate_perfect_logo_lighthouse_svg(size=1200):
    """
    Exact visual replica of the logo SVG:
    
    1. Gold Light Beams:
       - The beams are wide trapezoids expanding from the lantern room.
       - In the emblem, the beam edges go:
         Left: from (465, 375) to (10, 345) on top, and (465, 395) to (10, 420) on bottom.
         Right: from (535, 375) to (990, 345) on top, and (535, 395) to (990, 420) on bottom.
       - Color: #F3D593 -> #C19B4F.
       
    2. Lantern Room & Lamp:
       - Top platform cornice (white)
       - 3 glass panels (dark teal #214149) separated by vertical white mullions
       - Glowing golden lantern bulb in the center panel (#F3D593 with halo)
       - Lower gallery platform and railing with 5 vertical balusters
       
    3. Tower:
       - Tapered white masonry tower
       - Two-tone 3D shading:
         Left half is clean bright white (#FFFFFF)
         Right half is soft light-blue shadow (#E2EDF2)
       - 3 dark teal openings aligned vertically:
         - Top round window (arched)
         - Middle round window (arched)
         - Bottom entryway door (arched top)
         
    4. Rocky Island Base:
       - Pure white stylized rock island
       - Multiple dark teal (#214149) crevice contour lines following the natural form
       
    5. Water Reflections:
       - Inverted triangular stack of horizontal ripple lines below the island
       - Alternating crisp white (#FFFFFF) and aqua blue (#A5D2DF)
       - Lines progressively decrease in length downwards to create reflection perspective
    """
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="{size}" height="{size}">
  <defs>
    <!-- Gold Beam Gradients -->
    <linearGradient id="beamLeftGrad" x1="470" y1="385" x2="10" y2="385" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#F3D593" stop-opacity="0.95" />
      <stop offset="30%" stop-color="#C19B4F" stop-opacity="0.85" />
      <stop offset="100%" stop-color="#C19B4F" stop-opacity="0.60" />
    </linearGradient>

    <linearGradient id="beamRightGrad" x1="530" y1="385" x2="990" y2="385" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#F3D593" stop-opacity="0.95" />
      <stop offset="30%" stop-color="#C19B4F" stop-opacity="0.85" />
      <stop offset="100%" stop-color="#C19B4F" stop-opacity="0.60" />
    </linearGradient>

    <radialGradient id="bulbGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#FFFFFF" />
      <stop offset="35%" stop-color="#FFF2CD" />
      <stop offset="70%" stop-color="#F3D593" />
      <stop offset="100%" stop-color="#C19B4F" />
    </radialGradient>
  </defs>

  <g id="lighthouse_artwork">
    <!-- 1. Gold Light Beams -->
    <polygon points="466,374 10,342 10,422 466,396" fill="url(#beamLeftGrad)" />
    <polygon points="534,374 990,342 990,422 534,396" fill="url(#beamRightGrad)" />

    <!-- 2. Water Reflection Waves -->
    <g stroke-linecap="round">
      <line x1="170" y1="675" x2="830" y2="675" stroke="#A5D2DF" stroke-width="4.5" opacity="0.8" />
      <line x1="110" y1="691" x2="890" y2="691" stroke="#FFFFFF" stroke-width="5.5" opacity="0.95" />
      <line x1="150" y1="707" x2="850" y2="707" stroke="#A5D2DF" stroke-width="6" opacity="0.85" />
      <line x1="195" y1="723" x2="805" y2="723" stroke="#FFFFFF" stroke-width="5.5" opacity="0.95" />
      <line x1="250" y1="739" x2="750" y2="739" stroke="#A5D2DF" stroke-width="5.5" opacity="0.85" />
      <line x1="310" y1="755" x2="690" y2="755" stroke="#FFFFFF" stroke-width="5" opacity="0.9" />
      <line x1="370" y1="771" x2="630" y2="771" stroke="#A5D2DF" stroke-width="4.5" opacity="0.8" />
      <line x1="425" y1="787" x2="575" y2="787" stroke="#FFFFFF" stroke-width="4" opacity="0.85" />
      <line x1="460" y1="803" x2="540" y2="803" stroke="#A5D2DF" stroke-width="3.5" opacity="0.7" />
      <line x1="482" y1="819" x2="518" y2="819" stroke="#FFFFFF" stroke-width="3" opacity="0.6" />
    </g>

    <!-- 3. Rocky Base Island -->
    <path d="M 310 684
             C 330 670, 360 662, 390 660
             C 410 650, 425 642, 442 638
             L 558 638
             C 575 642, 590 650, 610 660
             C 640 662, 670 670, 690 684
             C 610 692, 390 692, 310 684 Z"
          fill="#FFFFFF" />

    <!-- Rock contour crevice lines (#214149) -->
    <path d="M 345 676 C 395 666, 450 672, 500 670 C 550 672, 605 666, 655 676" stroke="#214149" stroke-width="4.5" fill="none" stroke-linecap="round"/>
    <path d="M 390 663 C 430 654, 470 656, 500 654 C 530 656, 570 654, 610 663" stroke="#214149" stroke-width="3.5" fill="none" stroke-linecap="round"/>
    <path d="M 435 648 C 465 643, 500 644, 535 643 C 548 645, 558 647, 565 650" stroke="#214149" stroke-width="3" fill="none" stroke-linecap="round"/>

    <!-- 4. Tower Body -->
    <!-- Full Tower (White Left Side) -->
    <polygon points="445,638 464,426 536,426 555,638" fill="#FFFFFF" />

    <!-- Right Side Shadow Layer on Tower (#E1ECF0) -->
    <path d="M 500,426 L 536,426 L 555,638 L 500,638 Z" fill="#DCE7EC" />

    <!-- Tower Windows & Doors (Dark Navy #214149) -->
    <!-- Base Door with arched top -->
    <path d="M 488 620 L 488 584 C 488 576, 512 576, 512 584 L 512 620 Z" fill="#214149" />
    
    <!-- Middle Window with rounded top/bottom -->
    <rect x="489" y="498" width="22" height="34" rx="11" fill="#214149" />

    <!-- Upper Window with rounded top/bottom -->
    <rect x="490" y="442" width="20" height="28" rx="10" fill="#214149" />

    <!-- 5. Balcony / Gallery Platform (y=420..428) -->
    <rect x="446" y="420" width="108" height="8" rx="2" fill="#FFFFFF" />
    <line x1="446" y1="428" x2="554" y2="428" stroke="#214149" stroke-width="2" opacity="0.3"/>

    <!-- Balcony Railing (y=407..420) -->
    <!-- Top rail -->
    <line x1="448" y1="407" x2="552" y2="407" stroke="#FFFFFF" stroke-width="3.5" stroke-linecap="round"/>
    <!-- Middle wire -->
    <line x1="450" y1="414" x2="550" y2="414" stroke="#FFFFFF" stroke-width="2" />
    <!-- Vertical posts -->
    <line x1="452" y1="407" x2="452" y2="420" stroke="#FFFFFF" stroke-width="3" />
    <line x1="470" y1="407" x2="470" y2="420" stroke="#FFFFFF" stroke-width="2.5" />
    <line x1="488" y1="407" x2="488" y2="420" stroke="#FFFFFF" stroke-width="2.5" />
    <line x1="512" y1="407" x2="512" y2="420" stroke="#FFFFFF" stroke-width="2.5" />
    <line x1="530" y1="407" x2="530" y2="420" stroke="#FFFFFF" stroke-width="2.5" />
    <line x1="548" y1="407" x2="548" y2="420" stroke="#FFFFFF" stroke-width="3" />

    <!-- 6. Lantern Room Chamber (y=366..420) -->
    <rect x="464" y="366" width="72" height="42" fill="#FFFFFF" />
    <!-- Dark glass room interior -->
    <rect x="468" y="370" width="64" height="34" rx="2" fill="#214149" />
    
    <!-- Central Glowing Lamp / Bulb -->
    <circle cx="500" cy="387" r="11" fill="url(#bulbGlow)" />
    <rect x="496" y="370" width="8" height="34" fill="#F3D593" opacity="0.95"/>
    
    <!-- Window Vertical Mullions / Panes -->
    <line x1="482" y1="370" x2="482" y2="404" stroke="#FFFFFF" stroke-width="2.5" />
    <line x1="518" y1="370" x2="518" y2="404" stroke="#FFFFFF" stroke-width="2.5" />

    <!-- Lantern Cornice Platform -->
    <rect x="460" y="362" width="80" height="6" rx="2" fill="#FFFFFF" />

    <!-- 7. Lantern Dome / Cupola (y=332..362) -->
    <path d="M 464 362 
             C 464 336, 480 332, 500 332 
             C 520 332, 536 336, 536 362 Z" 
          fill="#FFFFFF" />
    <!-- Dome right half shadow (#DCE7EC) -->
    <path d="M 500 332 C 520 332, 536 336, 536 362 L 500 362 Z" fill="#DCE7EC" />

    <!-- 8. Spire & Finial (y=298..332) -->
    <rect x="495" y="322" width="10" height="11" rx="2" fill="#FFFFFF" />
    <circle cx="500" cy="316" r="7" fill="#FFFFFF" />
    <line x1="500" y1="298" x2="500" y2="312" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round"/>
  </g>
</svg>'''
    return svg

if __name__ == '__main__':
    svg_data = generate_perfect_logo_lighthouse_svg(1500)
    with open('/workspace/lighthouse_transparent.svg', 'w', encoding='utf-8') as f:
        f.write(svg_data)
    cairosvg.svg2png(url='/workspace/lighthouse_transparent.svg', write_to='/workspace/lighthouse_transparent.png', output_width=1500, output_height=1500)
    print("Exported updated lighthouse_transparent.svg & .png")
