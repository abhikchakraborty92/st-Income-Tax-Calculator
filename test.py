def calculate_hra_benefit(rent, basepay, hra, bpp):
    if rent > 0:
        c1 = rent - 0.1 * basepay
        c2 = bpp / 100 * basepay
        c3 = hra
        print(c1, c2, c3)
        return min(c1, c2, c3)
    else:
        return 0


if __name__ == "__main__":
    hra = 800000
    basepay = 1600000
    rent = 360000
    hrabenefit = calculate_hra_benefit(rent, basepay, hra, 40)
    print(hrabenefit)
