from PIL import Image, ImageDraw

def make_icon(size, filename):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    
    # Draw rounded rectangle background (purple-ish theme)
    r = size // 5
    d.rounded_rectangle([(0, 0), (size, size)], radius=r, fill="#cba6f7")
    
    # Draw a simple checkmark
    w = size // 10
    start = (size * 0.25, size * 0.5)
    mid = (size * 0.45, size * 0.7)
    end = (size * 0.75, size * 0.3)
    
    d.line([start, mid, end], fill="#1e1e2e", width=w, joint="curve")
    
    img.save(filename)

make_icon(192, 'static/icon-192.png')
make_icon(512, 'static/icon-512.png')
print("Icons generated!")
