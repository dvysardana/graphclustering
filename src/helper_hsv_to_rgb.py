__author__ = 'divya'


# input: HSV values in [0..1]
# returns [r, g, b] values from 0 to 255
def hsv_to_rgb(h, s, v):


    #s=0.3
    #v=0.99
    h_i = (int)(h*6)
    f = h*6 - h_i
    p = v * (1 - s)
    q = v * (1 - f*s)
    t = v * (1 - (1 - f) * s)
    if h_i==0:
        r, g, b = v, t, p
    elif h_i==1:
        r, g, b = q, v, p
    elif h_i==2:
        r, g, b = p, v, t
    elif h_i==3:
        r, g, b = p, q, v
    elif h_i==4:
        r, g, b = t, p, v
    elif h_i==5:
        r, g, b = v, p, q
    x = hex((int)(r*256))
    y = hex((int)(g*256))
    z = hex((int) (b*256))

    x = x[2:]
    y = y[2:]
    z = z[2:]

    if len(x)<2:
        x = "0" + x
    if len(y)<2:
        y = "0" + y
    if len(z)<2:
        z = "0" + z

    hex_color = x + y + z
    return "#" + hex_color.upper()