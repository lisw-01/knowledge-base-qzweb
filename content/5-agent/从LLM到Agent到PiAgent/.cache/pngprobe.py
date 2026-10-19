import zlib, struct, sys

def read_png(path):
    d = open(path, 'rb').read()
    assert d[:8] == b'\x89PNG\r\n\x1a\n'
    pos = 8
    idat = b''
    w = h = bitd = ct = None
    plte = None
    while pos < len(d):
        ln = struct.unpack('>I', d[pos:pos+4])[0]
        typ = d[pos+4:pos+8]
        data = d[pos+8:pos+8+ln]
        if typ == b'IHDR':
            w, h, bitd, ct, comp, filt, inter = struct.unpack('>IIBBBBB', data)
        elif typ == b'IDAT':
            idat += data
        elif typ == b'PLTE':
            plte = data
        elif typ == b'IEND':
            break
        pos += 12 + ln
    raw = zlib.decompress(idat)
    ch = {0:1, 2:3, 3:1, 4:2, 6:4}[ct]
    bpp = ch * (bitd // 8)
    stride = w * bpp
    out = bytearray()
    prev = bytearray(stride)
    i = 0
    for y in range(h):
        f = raw[i]; i += 1
        line = bytearray(raw[i:i+stride]); i += stride
        if f == 1:
            for x in range(bpp, stride):
                line[x] = (line[x] + line[x-bpp]) & 255
        elif f == 2:
            for x in range(stride):
                line[x] = (line[x] + prev[x]) & 255
        elif f == 3:
            for x in range(stride):
                a = line[x-bpp] if x >= bpp else 0
                line[x] = (line[x] + ((a + prev[x]) >> 1)) & 255
        elif f == 4:
            for x in range(stride):
                a = line[x-bpp] if x >= bpp else 0
                b = prev[x]
                c = prev[x-bpp] if x >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p-a), abs(p-b), abs(p-c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[x] = (line[x] + pr) & 255
        out += line
        prev = line
    return w, h, ch, bytes(out)

def px(w, h, ch, buf, x, y):
    o = (y*w + x)*ch
    return buf[o], buf[o+1], buf[o+2]

path = sys.argv[1]
w, h, ch, buf = read_png(path)
print(f'{path}: {w}x{h} ch={ch}')
for (x, y) in [(100,100),(400,60),(200,300),(700,250),(1000,400),(1200,680),(640,340),(60,660),(300,600)]:
    if x < w and y < h:
        r,g,b = px(w,h,ch,buf,x,y)
        print(f'  ({x},{y}) = ({r},{g},{b}) lum={0.299*r+0.587*g+0.114*b:.0f}')
# average luminance
tot=0; n=0
for y in range(0,h,7):
    for x in range(0,w,7):
        r,g,b=px(w,h,ch,buf,x,y); tot+=0.299*r+0.587*g+0.114*b; n+=1
print(f'  avg luminance = {tot/n:.1f}')
