import os
import cairosvg
from PIL import Image

def generate_exact_lighthouse_svg(size=1000, bg_color="#214149"):
    """
    Exact replica of the logo from the prompt:
    Circle at (500, 500) r=450.
    - Lantern center at y=380.
    - Rays:
      Left ray: from (470, 370) to (50, 365) and (470, 400) to (50, 420).
      Wait, looking closely at the original:
      Left beam top: (50, 368), bottom: (50, 425), inner top: (465, 372), inner bottom: (465, 398).
      Right beam top: (950, 368), bottom: (950, 425), inner top: (535, 372), inner bottom: (535, 398).
      Gradient: #F3D593 at the inner source fading slightly to #C19B4F towards the edges.
    
    - Rock:
      In the original, the white rock has an asymmetric natural shape:
      Left side is higher/steeper, right side is slightly flatter with a few crevices.
      Top of rock is under the tower: (420, 640) to (580, 640).
      Bottom of rock: (320, 690) to (680, 690).
      There are several distinct dark contour lines (#214149) carved into the rock.
      
    - Water lines:
      Parallel horizontal lines of varying widths:
      Line 1 (thin light blue #A5D2DF): (180, 680) to (820, 680)
      Line 2 (white #FFFFFF): (120, 695) to (880, 695)
      Line 3 (light blue #A5D2DF): (150, 710) to (850, 710)
      Line 4 (white #FFFFFF): (200, 725) to (800, 725)
      Line 5 (light blue #A5D2DF): (250, 740) to (750, 740)
      Line 6 (white #FFFFFF): (310, 755) to (690, 755)
      Line 7 (light blue #A5D2DF): (370, 770) to (630, 770)
      Line 8 (white #FFFFFF): (430, 785) to (570, 785)
      Line 9 (light blue #A5D2DF): (460, 800) to (540, 800)
    
    - Tower:
      Base: (448, 640) to (552, 640)
      Top: (466, 425) to (534, 425)
      Windows:
      Lower: door/window (490, 565) to (510, 615), rounded top
      Middle: window (490, 495) to (510, 535), rounded
      Upper: window (491, 442) to (509, 470), rounded
      Wait, on the tower there is also a dark shadow on the left or right side!
      In the original, the tower is white with subtle shadow or solid clean white.
      
    - Gallery:
      Platform: (450, 420) to (550, 428)
      Railing: posts at 456, 474, 500, 526, 544. Top rail connecting them.
    
    - Lantern:
      Glass room: (466, 368) to (534, 420)
      Glow: Central bright gold light bulb
    
    - Dome:
      Smooth curved dome (466, 368) curving up to (500, 335)
      Spire: tiered finial on top from y=335 up to y=300
    """
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="{size}" height="{size}">
  <defs>
    <clipPath id="circleClip">
      <circle cx="500" cy="500" r="450" />
    </clipPath>
    
    <!-- Linear gradient for gold light beams -->
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

  <!-- Dark Teal Circle Background: #214149 -->
  <circle cx="500" cy="500" r="450" fill="{bg_color}" />

  <g clip-path="url(#circleClip)">
    <!-- Golden Light Beams (expanding straight bands) -->
    <!-- Left Beam -->
    <polygon points="465,372 40,366 40,422 465,398" fill="url(#goldBeamL)" />
    <!-- Right Beam -->
    <polygon points="535,372 960,366 960,422 535,398" fill="url(#goldBeamR)" />

    <!-- Water Ripples (Stylized alternating lines) -->
    <g stroke-linecap="round">
      <line x1="180" y1="676" x2="820" y2="676" stroke="#A5D2DF" stroke-width="4.5" opacity="0.7" />
      <line x1="120" y1="692" x2="880" y2="692" stroke="#FFFFFF" stroke-width="5.5" opacity="0.95" />
      <line x1="160" y1="708" x2="840" y2="708" stroke="#A5D2DF" stroke-width="6" opacity="0.85" />
      <line x1="210" y1="724" x2="790" y2="724" stroke="#FFFFFF" stroke-width="5.5" opacity="0.9" />
      <line x1="265" y1="740" x2="735" y2="740" stroke="#A5D2DF" stroke-width="5.5" opacity="0.8" />
      <line x1="320" y1="756" x2="680" y2="756" stroke="#FFFFFF" stroke-width="5" opacity="0.85" />
      <line x1="380" y1="772" x2="620" y2="772" stroke="#A5D2DF" stroke-width="4.5" opacity="0.75" />
      <line x1="435" y1="788" x2="565" y2="788" stroke="#FFFFFF" stroke-width="4" opacity="0.7" />
      <line x1="465" y1="804" x2="535" y2="804" stroke="#A5D2DF" stroke-width="3.5" opacity="0.6" />
      <line x1="485" y1="820" x2="515" y2="820" stroke="#FFFFFF" stroke-width="3" opacity="0.5" />
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

    <!-- Lighthouse Tower Body (White) -->
    <polygon points="445,638 464,426 536,426 555,638" fill="#FFFFFF" />

    <!-- Vertical Accent / Subtle Shading -->
    <path d="M 500,426 L 536,426 L 555,638 L 500,638 Z" fill="#214149" opacity="0.04" />

    <!-- Tower Windows & Doors (Dark #214149) -->
    <!-- Base Door with arched top -->
    <path d="M 488 618 L 488 584 C 488 576, 512 576, 512 584 L 512 618 Z" fill="#214149" />
    
    <!-- Middle Window with rounded top/bottom -->
    <rect x="489" y="500" width="22" height="34" rx="11" fill="#214149" />

    <!-- Upper Window with rounded top/bottom -->
    <rect x="490" y="442" width="20" height="28" rx="10" fill="#214149" />

    <!-- Gallery / Balcony Platform -->
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

  <!-- Outer Ring Accent (#468A9D) -->
  <circle cx="500" cy="500" r="448" fill="none" stroke="#468A9D" stroke-width="4" opacity="0.5" />
</svg>'''
    return svg

if __name__ == '__main__':
    svg_str = generate_exact_lighthouse_svg(1000)
    with open('/workspace/lighthouse_exact.svg', 'w', encoding='utf-8') as f:
        f.write(svg_str)
    cairosvg.svg2png(url='/workspace/lighthouse_exact.svg', write_to='/workspace/lighthouse_exact.png', output_width=1000, output_height=1000)
    print("Exported lighthouse_exact.png!")
