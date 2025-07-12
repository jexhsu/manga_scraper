class LZString:
    @staticmethod
    def decompressFromBase64(input_str):
        """Decompress a base64-encoded LZString-compressed string"""
        if not input_str:
            return "" if input_str is None else None

        keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
        baseReverseDic = {ch: idx for idx, ch in enumerate(keyStr)}

        def getNextValue(index):
            return baseReverseDic[input_str[index]]

        return LZString._decompress(len(input_str), 32, getNextValue)

    @staticmethod
    def _decompress(length, resetValue, getNextValue):
        """Core LZ-string decompression logic"""
        dictionary = list(range(3))
        enlargeIn = 4
        dictSize = 4
        numBits = 3
        result = []
        entry = ""
        w = ""

        data = {"val": getNextValue(0), "position": resetValue, "index": 1}

        def readBits(n):
            bits, power = 0, 1
            for _ in range(n):
                resb = data["val"] & data["position"]
                data["position"] >>= 1
                if data["position"] == 0:
                    data["position"] = resetValue
                    data["val"] = getNextValue(data["index"])
                    data["index"] += 1
                bits |= (1 if resb > 0 else 0) * power
                power <<= 1
            return bits

        # Decode the first character
        next_val = readBits(2)
        if next_val == 0:
            c = chr(readBits(8))
        elif next_val == 1:
            c = chr(readBits(16))
        elif next_val == 2:
            return ""

        dictionary.append(c)
        result.append(c)
        w = c

        while True:
            if data["index"] > length:
                return ""

            c = readBits(numBits)

            if c == 0:
                dictionary.append(chr(readBits(8)))
                c = dictSize
                dictSize += 1
                enlargeIn -= 1
            elif c == 1:
                dictionary.append(chr(readBits(16)))
                c = dictSize
                dictSize += 1
                enlargeIn -= 1
            elif c == 2:
                return "".join(result)

            if enlargeIn == 0:
                enlargeIn = 2**numBits
                numBits += 1

            if c < len(dictionary) and dictionary[c] is not None:
                entry = dictionary[c]
            elif c == dictSize:
                entry = w + w[0]
            else:
                return None

            result.append(entry)
            dictionary.append(w + entry[0])
            dictSize += 1
            enlargeIn -= 1
            w = entry

            if enlargeIn == 0:
                enlargeIn = 2**numBits
                numBits += 1
