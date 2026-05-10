def f(p, n, g, s, e):
    if s == 1:
        c = 1.5
        tx = 0.1
        sr = 50
    elif s == 2:
        c = 1.2
        tx = 0.05
        sr = 30
    elif s == 3:
        c = 0.8
        tx = 0.0
        sr = 10
    else:
        c = 1.0
        tx = 0.0
        sr = 10

    r = p * n

    if g > 2:
        r = r + (g - 2) * 500
        if g > 4:
            r = r + (g - 4) * 300
            if g > 6:
                r = r + (g - 6) * 200

    if e == 1:
        r = r + 1000
    elif e == 2:
        r = r + 500
    elif e == 3:
        r = r + 1500

    r = r * c

    if n > 30:
        r = r * 0.85
    elif n > 14:
        r = r * 0.9
    elif n > 7:
        r = r * 0.95

    if p < 1000:
        r = r + 200
    elif p < 2000:
        r = r + 100
    elif p < 3000:
        r = r + 50

    r = r + r * tx

    if g > 2:
        r = r + 100
        if g > 4:
            r = r + 150
            if g > 6:
                r = r + 200

    d = 0
    if n % 7 == 0:
        d = 500
    elif n % 5 == 0:
        d = 300
    elif n % 3 == 0:
        d = 100

    r = r - d

    if e == 1:
        r = r + 200 + 50
    elif e == 2:
        r = r + 100 + 25

    if n > 30:
        r = r + 300
    elif n > 14:
        r = r + 200
    elif n > 7:
        r = r + 100

    if g > 2:
        r = r + 50
        if g > 4:
            r = r + 75
            if g > 6:
                r = r + 100

    print(r)

    return r