# -*- coding: utf-8 -*-

# thanks to this guy http://bazaar.launchpad.net/~ivanalert/vkunmask/0.1/view/head:/main.cpp
def vkunmask(mask):
    all = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN0PQRSTUVWXYZO123456789+/="
    mask = mask.split('#')
    
    def oFunc(_str):
        if _str == '' or len(_str)%4 == 1:
            return ''
        result = ''
        i = e = o = 0;
        for s in range(len(_str)):
            e = all.find(_str[s])
            if e < 0:
                continue
            i = (64 * i + e) if (o % 4) else e
            op = o+1
            if o % 4:
                result += chr(255 & i >> (-2 * op & 6))
            o = op
        return result
        
    def decode1(_str, i):
        o = all+all
        result = ''
        for s in reversed(range(len(_str))):
            e = o.find(_str[s])
            if e >= 0:
                if e >= i:
                    result = o[e - i] + result
                else:
                    result = o[len(o) - (i - e)] + result
            else:
                result = _str[s] + result
        return result
        
    def decode2(str1, str2):
        ch = ord(str2[0])
        result = ''
        for i in range(len(str1)):
            currCh = ord(str1[i])
            result += chr(0xFF & (currCh ^ ch))
        return result
    
    leftMask = oFunc(mask[0])
    rightMask = oFunc(mask[1])
    
    mask = rightMask.split('\x09')
    for it in reversed(mask):
        decodeStrs = it.split('\x0B')
        if decodeStrs[0] == 'v':
            leftMask = leftMask[::-1]
        elif decodeStrs[0] == 'r':
            leftMask = decode1(leftMask, int(decodeStrs[1]))
        elif decodeStrs[0] == 'x':
            leftMask = decode2(leftMask, decodeStrs[1])
            
    return leftMask

