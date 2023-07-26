#!/usr/bin/python3
# Copyright (c) 2021-2022, SIL International.
# Licensed under MIT license: https://opensource.org/licenses/MIT

import enum, re

class Cats(enum.Enum):
    Other = 0; Base = 1; Robat = 2; Coeng = 3; ZFCoeng = 4
    Shift = 5; Z = 6; VPre = 7; VB = 8; VA = 9
    VPost = 10; MS = 11; MF = 12

categories =  ([Cats.Base] * 35     # 1780-17A2
            + [Cats.Other] * 2      # 17A3-17A4
            + [Cats.Base] * 15      # 17A5-17B3
            + [Cats.Other] * 2      # 17B4-17B5
            + [Cats.VPost]          # 17B6
            + [Cats.VA] * 4         # 17B7-17BA
            + [Cats.VB] * 3         # 17BB-17BD
            + [Cats.VPre] * 8       # 17BE-17C5
            + [Cats.MS]             # 17C6
            + [Cats.MF] * 2         # 17C7-17C8
            + [Cats.Shift] * 2      # 17C9-17CA
            + [Cats.MS]             # 17CB
            + [Cats.Robat]          # 17CC
            + [Cats.MS] * 5         # 17CD-17D1
            + [Cats.Coeng]          # 17D2
            + [Cats.MS]             # 17D3
            + [Cats.Other] * 9      # 17D4-17DC
            + [Cats.MS])            # 17DD

khres = {   # useful regular sub expressions used later
    "B":       "[\u1780-\u17A2\u17A5-\u17B3\u25CC]",
    "NonRo":   "[\u1780-\u1799\u179B-\u17A2\u17A5-\u17B3]",
    "NonBA":   "[\u1780-\u1793\u1795-\u17A2\u17A5-\u17B3]",
    "S1":      "[\u1780-\u1783\u1785-\u1788\u178A-\u178D\u178F-\u1792"
               "\u1795-\u1797\u179E-\u17A0\u17A2]",
    "S2":      "[\u1784\u1780\u178E\u1793\u1794\u1798-\u179D\u17A1\u17A3-\u17B3]",
    "VAA":     "(?:[\u17B7-\u17BA\u17BE\u17BF\u17DD]|\u17B6\u17C6)",
    "VA":      "(?:[\u17C1-\u17C5]?{VAA})",
    "VAS":     "(?:{VA}|[\u17C1-\u17C3]?\u17D0)",
    "VB":      "(?:[\u17C1-\u17C3][\u17BB-\u17BD])",
    # contains series 1 and no BA
    "STRONG":  "{S1}\u17CC?(?:\u17D2{NonBA}(?:\u17D2{NonBA})?)?|"
               "{NonBA}\u17CC?(?:\u17D2{S1}(?:\u17D2{NonBA})?|\u17D2{NonBA}\u17D2{S1})",
    # contains BA or only series 2
    "NSTRONG": "(?:{S2}\u17CC?(?:\u17D2{S2}(?:\u17D2{S2})?)?|\u1794\u17CC?{COENG}?|"
               "{B}\u17CC?(?:\u17D2{NonRo}\u17D2\u1794|\u17D2\u1794(?:\u17D2{B}))?)",
    "COENG":   "(?:(?:\u17D2{NonRo})?\u17D2{B})",
    # final right spacing coeng
    "COENGR":  "(?:(?:[\u17C9\u17CA]\u200C?)?(?:{VB}?{VAS}|{VB}))",
    # final all coengs
    "COENGF":  "(?:(?:[\u17C9\u17CA]\u200C?)?[\u17C2-\u17C3]?{VB}?{VA}?"
               "[\u17B6\u17BF\u17C0\u17C4\u17C5])",
    "COENGS":  "(?:\u17C9\u200C?{VAS})",
    "FCOENG":  "(?:\u17D2\u200D{NonRo})",
    "SHIFT":   "(?:(?<={STRONG}{FCOENG}?)\u17CA\u200C(?={VA})|"
               "(?<={NSTRONG}{FCOENG}?)\u17C9\u200C(?={VAS})|[\u17C9\u17CA])",
    "V":       "(?:\u17C1[\u17BC\u17BD]?[\u17B7\u17B9\u17BA]?|"
               "[\u17C2\u17C3]?[\u17BC\u17BD]?[\u17B7-\u17BA]\u17B6|"
               "[\u17C2\u17C3]?[\u17BB-\u17BD]?\u17B6|\u17BE[\u17BC\u17BD]?\u17B6?|"
               "[\u17C1-\u17C5]?\u17BB(?![\u17D0\u17DD])|"
               "[\u17BF\u17C0]|[\u17C2-\u17C5]?[\u17BC\u17BD]?[\u17B7-\u17BA]?)",
    "MS":      "(?:(?:[\u17C6\u17CB\u17CD-\u17CF\u17D1\u17D3]|"
               "(?<!\u17BB[\u17B6\u17C4\u17C5]?)[\u17D0\u17DD])"
               "[\u17C6\u17CB\u17CD-\u17D1\u17D3\u17DD]?)"
}

# expand 2 times: CEONGS -> VAS -> VA -> VAA
for i in range(3):
    khres = {k: v.format(**khres) for k, v in khres.items()}

def charcat(c):
    ''' Returns the Khmer character category for a single char string'''
    o = ord(c)
    if 0x1780 <= o <= 0x17DD:
        return categories[o-0x1780]
    elif o == 0x200C:
        return Cats.Z
    elif o == 0x200D:
        return Cats.ZFCoeng
    return Cats.Other

def khmer_normalize(txt, lang="km"):
    ''' Returns khmer normalised string, without fixing or marking errors'''
    # Mark final coengs in Middle Khmer
    if lang == "xhm":
        txt = re.sub(r"([\u17B7-\u17C5]\u17D2)", "\\1\u200D", txt)
    # Categorise every character in the string
    charcats = [charcat(c) for c in txt]

    # Recategorise base or ZWJ -> coeng after coeng char
    for i in range(1, len(charcats)):
        if charcats[i-1] == Cats.Coeng and charcats[i] in (Cats.Base, Cats.ZFCoeng):
            charcats[i] = Cats.Coeng

    # Find subranges of base+non other and sort components in the subrange
    i = 0
    res = []
    while i < len(charcats):
        c = charcats[i]
        if c != Cats.Base:
            res.append(txt[i])
            i += 1
            continue
        # Scan for end of syllable
        j = i + 1
        while j < len(charcats) and charcats[j].value > Cats.Base.value:
            j += 1
        # Sort syllable based on character categories
        # Sort the char indices by category then position in string
        newindices = sorted(range(i, j), key=lambda e:(charcats[e].value, e))
        replaces = "".join(txt[n] for n in newindices)

        replaces = re.sub("([\u200C\u200D]\u17D2?|\u17D2\u200D)[\u17D2\u200C\u200D]+",
                          r"\1", replaces)      # remove multiple invisible chars
        # map compoound vowel sequences to compounds with -u before to be converted
        replaces = re.sub("\u17C1([\u17BB-\u17BD]?)\u17B8", "\u17BE\\1", replaces)
        replaces = re.sub("\u17C1([\u17BB-\u17BD]?)\u17B6", "\u17C4\\1", replaces)
        replaces = re.sub("(\u17BE)(\u17BB)", r"\2\1", replaces)
        # Replace -u + upper vowel with consonant shifter
        replaces = re.sub("({STRONG}{FCOENG}?[\u17C1-\u17C5]?)\u17BB"
                          "(?={VAA}|\u17D0)".format(**khres), "\\1\u17CA", replaces)
        replaces = re.sub("({NSTRONG}{FCOENG}?[\u17C1-\u17C5]?)\u17BB"
                          "(?={VAA}|\u17D0)".format(**khres), "\\1\u17C9", replaces)
        replaces = re.sub("(\u17D2\u179A)(\u17D2[\u1780-\u17B3])",
                          r"\2\1", replaces)    # coeng ro second
        replaces = re.sub("(\u17D2)\u178A", "\\1\u178F", replaces)  # coeng da->ta
        res.append(replaces)
        i = j
    return "".join(res)

def khtest(txt):
    ''' Tests normalized text for conformance to Khmer encoding structure '''
    import regex
    syl = regex.compile("({B}\u17CC?{COENG}?(?:\u17D2\u200D(?={COENGR})|{FCOENG}(?={COENGF})|"
           "(?<={NSTRONG})\u17D2\u200D{S1}(?={COENGS}))?{SHIFT}?{V}{MS}?[\u17C7\u17C8]?|"
           "[\u17A3\u17A4\u17B4\u17B5]|[^\u1780-\u17D2])".format(**khres))
    res = []
    passed = True
    while len(txt):
        m = syl.match(txt)          # match a syllable
        if m:
            res.append(m.group(1))  # add matched syllable to output
            txt = txt[m.end(1):]    # update start to after this syllable
            continue                # go round for the next syllable
        passed = False                          # will return a failed string
        m = syl.match("\u25CC"+txt)             # Try inserting 25CC and matching that
        if m and m.end(1) > 1:
            res.append(m.group(1))     # yes then insert 25CC in output
            txt = txt[m.end(1)-1:]
        else:
            res.append("!{}!".format(txt[0]))   # output failure character
            txt = txt[1:]
    if not passed:                  # if the output is different, return it
        return "".join(res)
    return None                     # return None as sentinal for pass