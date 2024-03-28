# import base64
#
# encoded_string = "bqCbtIAPI2JXLhmzFzfIjnvzoMZsCx+yCElEKuPJ5qkSV9k0V3hR4mhc8jSYMZBNAU+VQILGbqFT33GwUrHMCQ=="
# decoded_bytes = base64.b64decode(encoded_string)
# print(decoded_bytes)
# decoded_string = decoded_bytes.decode('latin1')
#
# print(decoded_string)
#
# import chardet
#
# rawdata = "qQtkZgxSjBYs70VnKLiduXQTUzxVkECY9NWn5ISzzY2K70uEtEWsJHzqHrAAkuPQmJewPA22iqMZQqzXWa/7pTOE2GRCl5Cd0d3hTX2cYkPi2gblMrubRVhM9wSXCCZaDMP31BC2KUTa2s+/mpazOJTVOntw+xuFpuJVgNRQ8LXmgnlXHSWOfHySiAO5kiBx"
# meta = chardet.detect(rawdata)
# try:
#     rawdata.decode(meta['encoding'])
#     print(rawdata.decode(meta['encoding']))
#     print(meta)
# except Exception as KeyError:
#     print('Кодировка не известна')

encoded_string = "\\u0417\\u0430\\u043f\\u0438\\u0441\\u0430\\u043b"
decoded_string = encoded_string.encode('utf-8').decode('unicode-escape')

print(decoded_string)